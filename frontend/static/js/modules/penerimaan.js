/**
 * Modul Penerimaan — Jenis Pembayaran, Tagihan (akrual piutang), Pembayaran/Cicilan.
 * Mengikuti pola yang sama dengan ReferensiModule/SiswaModule (constructor, render(), destroy()).
 */
class PenerimaanModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'jenis-pembayaran'; // jenis-pembayaran | tagihan | pembayaran
    this._departemenCache = null;
    this._akunCache = null;
    this._siswaCache = null;
    this._tahunBukuCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Penerimaan</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;">
        ${this._renderTabButton('jenis-pembayaran', 'Jenis Pembayaran')}
        ${this._renderTabButton('tagihan', 'Tagihan')}
        ${this._renderTabButton('pembayaran', 'Pembayaran')}
      </div>
      <div class="panel">
        <div class="panel__header">
          <span class="text-muted">Daftar ${this._judulTab()}</span>
          ${this.tab !== 'pembayaran' ? '<button class="btn btn-primary btn-sm" id="btn-tambah">+ Tambah</button>' : ''}
        </div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;

    this.container.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => router.navigate(`penerimaan/${btn.dataset.tab}`));
    });
    const btnTambah = this.container.querySelector('#btn-tambah');
    if (btnTambah) btnTambah.addEventListener('click', () => this._bukaFormTambah());

    await this._muatData();
  }

  _judulTab() {
    return {
      'jenis-pembayaran': 'Jenis Pembayaran',
      tagihan: 'Tagihan',
      pembayaran: 'Pembayaran',
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

  async _muatSiswa() {
    if (!this._siswaCache) this._siswaCache = await this.api.get('/siswa/siswa');
    return this._siswaCache;
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
      if (this.tab === 'jenis-pembayaran') {
        const data = await this.api.get('/penerimaan/jenis-pembayaran');
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama' },
          { key: 'nominal_default', label: 'Nominal Default', type: 'uang' },
          { key: 'aktif', label: 'Aktif', type: 'badge', badgeMap: { true: 'success', false: 'neutral' } },
        ], data, { emptyMessage: 'Belum ada jenis pembayaran. Tambahkan dulu (mis. SPP, Uang Gedung).' });
      } else if (this.tab === 'tagihan') {
        const data = await this.api.get('/penerimaan/tagihan');
        target.innerHTML = TableRenderer.render([
          { key: 'no_tagihan', label: 'No. Tagihan' },
          { key: 'tanggal', label: 'Tanggal' },
          { key: 'jumlah_tagihan', label: 'Jumlah', type: 'uang' },
          { key: 'diskon', label: 'Diskon', type: 'uang' },
          { key: 'sisa', label: 'Sisa', type: 'uang' },
          { key: 'status', label: 'Status', type: 'badge', badgeMap: {
              BELUM_LUNAS: 'warning', LUNAS: 'success', DIBATALKAN: 'danger',
          } },
          { key: 'aksi', label: '', type: 'aksi', render: (row) => row.status === 'BELUM_LUNAS'
              ? `<button class="btn btn-outline btn-sm" data-bayar="${row.id}">Bayar</button>`
              : '' },
        ], data, { emptyMessage: 'Belum ada tagihan. Tambahkan dulu lewat tombol + Tambah.' });

        target.querySelectorAll('[data-bayar]').forEach(btn => {
          btn.addEventListener('click', () => this._bukaFormBayar(Number(btn.dataset.bayar)));
        });
      } else if (this.tab === 'pembayaran') {
        const data = await this.api.get('/penerimaan/pembayaran');
        target.innerHTML = TableRenderer.render([
          { key: 'tanggal', label: 'Tanggal' },
          { key: 'jumlah_bayar', label: 'Jumlah Bayar', type: 'uang' },
          { key: 'status', label: 'Status', type: 'badge', badgeMap: { AKTIF: 'success', DIBATALKAN: 'danger' } },
          { key: 'keterangan', label: 'Keterangan' },
        ], data, { emptyMessage: 'Belum ada pembayaran tercatat.' });
      }
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  async _bukaFormTambah() {
    const departemen = await this._muatDepartemen();
    const departemenOptions = departemen.map(d => ({ value: d.id, label: d.nama }));

    if (this.tab === 'jenis-pembayaran') {
      const akun = await this._muatAkun();
      Modal.open({
        title: 'Tambah Jenis Pembayaran',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'kode', label: 'Kode (mis. SPP)', required: true },
          { name: 'nama', label: 'Nama (mis. SPP Bulanan)', required: true },
          { name: 'akun_piutang_id', label: 'Akun Piutang', type: 'select', required: true,
            options: akun.map(a => ({ value: a.id, label: `${a.kode} - ${a.nama}` })) },
          { name: 'akun_pendapatan_id', label: 'Akun Pendapatan', type: 'select', required: true,
            options: akun.map(a => ({ value: a.id, label: `${a.kode} - ${a.nama}` })) },
          { name: 'nominal_default', label: 'Nominal Default', type: 'uang' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/penerimaan/jenis-pembayaran', {
            ...data,
            departemen_id: Number(data.departemen_id),
            akun_piutang_id: Number(data.akun_piutang_id),
            akun_pendapatan_id: Number(data.akun_pendapatan_id),
            nominal_default: data.nominal_default || null,
          });
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'tagihan') {
      const [siswa, jenis, akun, tahunBuku] = await Promise.all([
        this._muatSiswa(), this.api.get('/penerimaan/jenis-pembayaran'), this._muatAkun(), this._muatTahunBuku(),
      ]);
      if (!siswa.length) {
        window.alert('Belum ada Siswa. Tambahkan dulu di modul Siswa & Calon Siswa.');
        return;
      }
      if (!jenis.length) {
        window.alert('Belum ada Jenis Pembayaran. Tambahkan dulu di tab Jenis Pembayaran.');
        return;
      }
      const aktif = this._tahunBukuAktif(tahunBuku);
      if (!aktif) {
        window.alert('Belum ada Tahun Buku aktif. Buat dulu di modul Referensi.');
        return;
      }
      Modal.open({
        title: 'Tambah Tagihan',
        bodyHtml: FormBuilder.render([
          { name: 'siswa_id', label: 'Siswa', type: 'select', required: true,
            options: siswa.map(s => ({ value: s.id, label: `${s.nis} - ${s.nama}` })) },
          { name: 'jenis_pembayaran_id', label: 'Jenis Pembayaran', type: 'select', required: true,
            options: jenis.map(j => ({ value: j.id, label: j.nama })) },
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'tanggal', label: 'Tanggal', type: 'date', required: true },
          { name: 'jumlah_tagihan', label: 'Jumlah Tagihan', type: 'uang', required: true },
          { name: 'diskon', label: 'Diskon', type: 'uang' },
          { name: 'langsung_lunas', label: 'Lunas langsung (tanpa proses piutang)', type: 'checkbox' },
          { name: 'akun_kas_id', label: 'Akun Kas (wajib kalau lunas langsung)', type: 'select',
            options: akun.map(a => ({ value: a.id, label: `${a.kode} - ${a.nama}` })) },
          { name: 'keterangan', label: 'Keterangan', type: 'textarea' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post(`/penerimaan/tagihan?petugas_id=1`, { // TODO: ganti ke user login saat modul Pengaturan jadi
            siswa_id: Number(data.siswa_id),
            jenis_pembayaran_id: Number(data.jenis_pembayaran_id),
            departemen_id: Number(data.departemen_id),
            tahun_buku_id: aktif.id,
            tanggal: data.tanggal,
            jumlah_tagihan: data.jumlah_tagihan,
            diskon: data.diskon || '0',
            langsung_lunas: !!data.langsung_lunas,
            akun_kas_id: data.akun_kas_id ? Number(data.akun_kas_id) : null,
            keterangan: data.keterangan || null,
          });
          close();
          this._muatData();
        },
      });
    }
  }

  async _bukaFormBayar(tagihanId) {
    const [akun, tahunBuku, tagihanList] = await Promise.all([
      this._muatAkun(), this._muatTahunBuku(), this.api.get('/penerimaan/tagihan'),
    ]);
    const tagihan = tagihanList.find(t => t.id === tagihanId);
    const aktif = this._tahunBukuAktif(tahunBuku);
    if (!aktif) {
      window.alert('Belum ada Tahun Buku aktif. Buat dulu di modul Referensi.');
      return;
    }
    Modal.open({
      title: `Bayar Tagihan ${tagihan.no_tagihan} (Sisa: ${TableRenderer.formatUang(tagihan.sisa)})`,
      bodyHtml: FormBuilder.render([
        { name: 'jumlah_bayar', label: 'Jumlah Bayar', type: 'uang', required: true, value: tagihan.sisa },
        { name: 'akun_kas_id', label: 'Akun Kas', type: 'select', required: true,
          options: akun.map(a => ({ value: a.id, label: `${a.kode} - ${a.nama}` })) },
        { name: 'tanggal', label: 'Tanggal', type: 'date', required: true },
        { name: 'keterangan', label: 'Keterangan', type: 'textarea' },
      ]),
      onSubmit: async (data, close) => {
        await this.api.post(`/penerimaan/pembayaran?petugas_id=1`, { // TODO: ganti ke user login saat modul Pengaturan jadi
          tagihan_id: tagihanId,
          tahun_buku_id: aktif.id, // tahun buku AKTIF saat pembayaran terjadi, bukan tahun buku tagihan asal
          tanggal: data.tanggal,
          jumlah_bayar: data.jumlah_bayar,
          akun_kas_id: Number(data.akun_kas_id),
          keterangan: data.keterangan || null,
        });
        close();
        this._muatData();
      },
    });
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
