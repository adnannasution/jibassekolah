/**
 * Modul Referensi — Departemen, Kode Rekening Perkiraan (Akun), Tahun Buku.
 * Pola di sini adalah TEMPLATE untuk modul-modul berikutnya: konstruktor terima
 * (container, api, params), render() async, destroy() lepas listener kalau ada.
 */
class ReferensiModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'departemen'; // departemen | akun | tahun-buku
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Referensi</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4);">
        ${this._renderTabButton('departemen', 'Departemen')}
        ${this._renderTabButton('akun', 'Kode Rekening Perkiraan')}
        ${this._renderTabButton('tahun-buku', 'Tahun Buku')}
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
      btn.addEventListener('click', () => router.navigate(`referensi/${btn.dataset.tab}`));
    });
    this.container.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());

    await this._muatData();
  }

  _judulTab() {
    return { departemen: 'Departemen', akun: 'Kode Rekening Perkiraan', 'tahun-buku': 'Tahun Buku' }[this.tab];
  }

  _renderTabButton(key, label) {
    const active = this.tab === key ? 'btn-primary' : 'btn-outline';
    return `<button class="btn ${active} btn-sm" data-tab="${key}">${label}</button>`;
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    try {
      if (this.tab === 'departemen') {
        const data = await this.api.get('/referensi/departemen');
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama' },
          { key: 'aktif', label: 'Status', type: 'badge', badgeMap: { true: 'success', false: 'neutral' } },
        ], data, { emptyMessage: 'Belum ada departemen. Tambahkan dulu (mis. SMA, SMP, TK).' });
      } else if (this.tab === 'akun') {
        const data = await this.api.get('/referensi/akun');
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama Akun' },
          { key: 'kategori', label: 'Kategori', type: 'badge', badgeMap: {
              HARTA: 'success', PIUTANG: 'warning', INVENTARIS: 'neutral',
              UTANG: 'danger', MODAL: 'success', PENDAPATAN: 'success', BIAYA: 'danger',
          } },
        ], data, { emptyMessage: 'Belum ada Kode Rekening Perkiraan.' });
      } else if (this.tab === 'tahun-buku') {
        const data = await this.api.get('/referensi/tahun-buku');
        target.innerHTML = TableRenderer.render([
          { key: 'tahun_buku', label: 'Tahun Buku' },
          { key: 'tanggal_mulai', label: 'Tanggal Mulai' },
          { key: 'awalan_kuitansi', label: 'Awalan Kuitansi' },
          { key: 'status', label: 'Status', type: 'badge', badgeMap: { AKTIF: 'success', TUTUP: 'neutral' } },
          { key: 'aksi', label: '', type: 'aksi', render: (row) =>
              row.status === 'AKTIF'
                ? `<button class="btn btn-outline btn-sm" data-tutup-buku="${row.id}">Tutup Buku</button>`
                : ''
          },
        ], data, { emptyMessage: 'Belum ada Tahun Buku untuk departemen ini.' });

        target.querySelectorAll('[data-tutup-buku]').forEach(btn => {
          btn.addEventListener('click', () => this._bukaFormTutupBuku(
            data.find(d => d.id === Number(btn.dataset.tutupBuku))
          ));
        });
      }
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  async _bukaFormTambah() {
    if (this.tab === 'departemen') {
      Modal.open({
        title: 'Tambah Departemen',
        bodyHtml: FormBuilder.render([
          { name: 'kode', label: 'Kode (mis. SMA)', required: true },
          { name: 'nama', label: 'Nama Departemen', required: true },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/referensi/departemen', { kode: data.kode, nama: data.nama, aktif: true });
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'akun') {
      Modal.open({
        title: 'Tambah Kode Rekening Perkiraan',
        bodyHtml: FormBuilder.render([
          { name: 'kategori', label: 'Kategori', type: 'select', required: true, options: [
            'HARTA', 'PIUTANG', 'INVENTARIS', 'UTANG', 'MODAL', 'PENDAPATAN', 'BIAYA',
          ].map(v => ({ value: v, label: v })) },
          { name: 'kode', label: 'Kode (mis. H-001)', required: true },
          { name: 'nama', label: 'Nama Akun', required: true },
          { name: 'keterangan', label: 'Keterangan', type: 'textarea' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/referensi/akun', data);
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'tahun-buku') {
      const departemen = await this.api.get('/referensi/departemen');
      Modal.open({
        title: 'Tambah Tahun Buku',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true,
            options: departemen.map(d => ({ value: d.id, label: d.nama })) },
          { name: 'tahun_buku', label: 'Tahun Buku (mis. 2025/2026)', required: true },
          { name: 'tanggal_mulai', label: 'Tanggal Mulai', type: 'date', required: true },
          { name: 'awalan_kuitansi', label: 'Awalan Kuitansi', required: true },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/referensi/tahun-buku', { ...data, departemen_id: Number(data.departemen_id) });
          close();
          this._muatData();
        },
      });
    }
  }

  async _bukaFormTutupBuku(tahunBukuAktif) {
    const akunList = await this.api.get('/referensi/akun?kategori=MODAL');
    if (!akunList.length) {
      window.alert('Belum ada akun kategori MODAL. Tambahkan dulu akun Laba Ditahan di tab Kode Rekening Perkiraan.');
      return;
    }
    Modal.open({
      title: `Tutup Buku — ${tahunBukuAktif.tahun_buku}`,
      submitLabel: 'Proses Tutup Buku',
      bodyHtml: `
        <p class="text-muted" style="margin-top:0">
          Tahun buku lama akan dikunci dan tidak bisa diakses lagi untuk transaksi baru
          setelah tahun buku baru dibuat.
        </p>
        ${FormBuilder.render([
          { name: 'tahun_buku_baru', label: 'Tahun Buku Baru (mis. 2026/2027)', required: true },
          { name: 'tanggal_mulai_baru', label: 'Tanggal Mulai Periode Baru', type: 'date', required: true },
          { name: 'awalan_kuitansi_baru', label: 'Awalan Kuitansi Baru', required: true },
          { name: 'akun_retained_earning_id', label: 'Akun Laba Ditahan (Retained Earning)', type: 'select', required: true,
            options: akunList.map(a => ({ value: a.id, label: `${a.kode} — ${a.nama}` })) },
          { name: 'keterangan', label: 'Keterangan', type: 'textarea' },
        ])}
      `,
      onSubmit: async (data, close) => {
        const hasil = await this.api.post(
          `/referensi/tutup-buku?petugas_id=${Auth.userId()}`,
          {
            departemen_id: tahunBukuAktif.departemen_id,
            tahun_buku_lama_id: tahunBukuAktif.id,
            tahun_buku_baru: data.tahun_buku_baru,
            tanggal_mulai_baru: data.tanggal_mulai_baru,
            awalan_kuitansi_baru: data.awalan_kuitansi_baru,
            akun_retained_earning_id: Number(data.akun_retained_earning_id),
            keterangan: data.keterangan || null,
          }
        );
        close();
        window.alert(
          `Tutup buku berhasil.\nLaba/rugi ${tahunBukuAktif.tahun_buku}: Rp ${TableRenderer.formatUang(hasil.laba_rugi_tahun_lama)}\nTahun buku aktif sekarang: ${hasil.tahun_buku_baru}`
        );
        this._muatData();
      },
    });
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
    // Pola ini wajib ada di tiap modul untuk konsistensi dengan Router.
  }
}
