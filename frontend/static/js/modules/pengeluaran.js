/**
 * Modul Pengeluaran — Jenis Pengeluaran (mapping akun tetap) dan Pengeluaran (transaksi+kuitansi).
 * Mengikuti pola yang sama dengan PenerimaanModule (constructor, render(), destroy()).
 */
class PengeluaranModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'jenis-pengeluaran'; // jenis-pengeluaran | pengeluaran
    this._departemenCache = null;
    this._akunCache = null;
    this._tahunBukuCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Pengeluaran</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;">
        ${this._renderTabButton('jenis-pengeluaran', 'Jenis Pengeluaran')}
        ${this._renderTabButton('pengeluaran', 'Pengeluaran')}
      </div>
      <div class="panel">
        <div class="panel__header">
          <span class="text-muted">Daftar ${this._judulTab()}</span>
          <button class="btn btn-primary btn-sm" id="btn-tambah">+ Tambah</button>
        </div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;

    this.container.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => router.navigate(`pengeluaran/${btn.dataset.tab}`));
    });
    this.container.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());

    await this._muatData();
  }

  _judulTab() {
    return {
      'jenis-pengeluaran': 'Jenis Pengeluaran',
      pengeluaran: 'Pengeluaran',
    }[this.tab];
  }

  _renderTabButton(key, label) {
    const active = this.tab === key ? 'btn-primary' : 'btn-outline';
    return `<button class="btn ${active} btn-sm" data-tab="${key}">${label}</button>`;
  }

  async _muatDepartemen() {
    if (!this._departemenCache) this._departemenCache = await this.api.get('/referensi/departemen');
    return this._departemenCache;
  }

  async _muatAkun() {
    if (!this._akunCache) this._akunCache = await this.api.get('/referensi/akun');
    return this._akunCache;
  }

  async _muatTahunBuku() {
    if (!this._tahunBukuCache) this._tahunBukuCache = await this.api.get('/referensi/tahun-buku');
    return this._tahunBukuCache;
  }

  _tahunBukuAktif(daftar) {
    return daftar.find(t => t.status === 'AKTIF');
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    try {
      if (this.tab === 'jenis-pengeluaran') {
        const data = await this.api.get('/pengeluaran/jenis-pengeluaran');
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama' },
          { key: 'nominal_default', label: 'Nominal Default', type: 'uang' },
          { key: 'aktif', label: 'Aktif', type: 'badge', badgeMap: { true: 'success', false: 'neutral' } },
        ], data, { emptyMessage: 'Belum ada jenis pengeluaran. Tambahkan dulu (mis. ATK, Listrik).' });
      } else if (this.tab === 'pengeluaran') {
        const data = await this.api.get('/pengeluaran/pengeluaran');
        target.innerHTML = TableRenderer.render([
          { key: 'no_kuitansi', label: 'No. Kuitansi' },
          { key: 'tanggal', label: 'Tanggal' },
          { key: 'jumlah', label: 'Jumlah', type: 'uang' },
          { key: 'keterangan', label: 'Keterangan' },
          { key: 'status', label: 'Status', type: 'badge', badgeMap: { AKTIF: 'success', DIBATALKAN: 'danger' } },
          { key: 'aksi', label: '', type: 'aksi', render: (row) => row.status === 'AKTIF'
              ? `<button class="btn btn-outline btn-sm" data-batal="${row.id}">Batalkan</button>`
              : '' },
        ], data, { emptyMessage: 'Belum ada pengeluaran. Tambahkan dulu lewat tombol + Tambah.' });

        target.querySelectorAll('[data-batal]').forEach(btn => {
          btn.addEventListener('click', () => this._batalkanPengeluaran(Number(btn.dataset.batal)));
        });
      }
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  async _bukaFormTambah() {
    const departemen = await this._muatDepartemen();
    const departemenOptions = departemen.map(d => ({ value: d.id, label: d.nama }));

    if (this.tab === 'jenis-pengeluaran') {
      const akun = await this._muatAkun();
      Modal.open({
        title: 'Tambah Jenis Pengeluaran',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'kode', label: 'Kode (mis. ATK)', required: true },
          { name: 'nama', label: 'Nama (mis. Pembelian ATK)', required: true },
          { name: 'akun_kas_id', label: 'Akun Kas (rek. kredit)', type: 'select', required: true,
            options: akun.map(a => ({ value: a.id, label: `${a.kode} - ${a.nama}` })) },
          { name: 'akun_biaya_id', label: 'Akun Biaya (rek. debet)', type: 'select', required: true,
            options: akun.map(a => ({ value: a.id, label: `${a.kode} - ${a.nama}` })) },
          { name: 'nominal_default', label: 'Nominal Default', type: 'uang' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/pengeluaran/jenis-pengeluaran', {
            ...data,
            departemen_id: Number(data.departemen_id),
            akun_kas_id: Number(data.akun_kas_id),
            akun_biaya_id: Number(data.akun_biaya_id),
            nominal_default: data.nominal_default || null,
          });
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'pengeluaran') {
      const [jenis, tahunBuku] = await Promise.all([
        this.api.get('/pengeluaran/jenis-pengeluaran'), this._muatTahunBuku(),
      ]);
      if (!jenis.length) {
        Modal.alert('Belum ada Jenis Pengeluaran. Tambahkan dulu di tab Jenis Pengeluaran.');
        return;
      }
      const aktif = this._tahunBukuAktif(tahunBuku);
      if (!aktif) {
        Modal.alert('Belum ada Tahun Buku aktif. Buat dulu di modul Referensi.');
        return;
      }
      Modal.open({
        title: 'Tambah Pengeluaran',
        bodyHtml: FormBuilder.render([
          { name: 'jenis_pengeluaran_id', label: 'Jenis Pengeluaran', type: 'select', required: true,
            options: jenis.map(j => ({ value: j.id, label: j.nama })) },
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'tanggal', label: 'Tanggal', type: 'date', required: true },
          { name: 'jumlah', label: 'Jumlah', type: 'uang', required: true },
          { name: 'keterangan', label: 'Keterangan', type: 'textarea' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post(`/pengeluaran/pengeluaran?petugas_id=${Auth.userId()}`, {
            jenis_pengeluaran_id: Number(data.jenis_pengeluaran_id),
            departemen_id: Number(data.departemen_id),
            tahun_buku_id: aktif.id,
            tanggal: data.tanggal,
            jumlah: data.jumlah,
            keterangan: data.keterangan || null,
          });
          close();
          this._muatData();
        },
      });
    }
  }

  async _batalkanPengeluaran(pengeluaranId) {
    const alasan = window.prompt('Alasan pembatalan pengeluaran ini:');
    if (!alasan) return;
    try {
      await this.api.post(`/pengeluaran/pengeluaran/${pengeluaranId}/batalkan?user_id=${Auth.userId()}`, { alasan });
      this._muatData();
    } catch (err) {
      Modal.alert(`Gagal membatalkan: ${err.message}`);
    }
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
