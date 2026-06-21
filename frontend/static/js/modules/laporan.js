/**
 * Modul Laporan Keuangan — Buku Besar, Neraca Percobaan, Rugi Laba, Neraca,
 * Perubahan Modal, Arus Kas, Audit Perubahan Data. SEMUA laporan ini query
 * langsung dari jurnal_detail di backend (lihat app/core/laporan.py), bukan
 * tabel hasil hitung terpisah, sesuai prinsip desain di CLAUDE.md.
 */
class LaporanModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'neraca-percobaan';
    this._tahunBukuCache = null;
    this._akunCache = null;
    this._tahunBukuId = null;
    this._akunIdBukuBesar = null;
    this._pgBukuBesar = { cari: '', halaman: 1 };
  }

  async render() {
    const tahunBuku = await this._muatTahunBuku();
    if (!this._tahunBukuId) {
      const aktif = tahunBuku.find(t => t.status === 'AKTIF');
      this._tahunBukuId = aktif ? aktif.id : (tahunBuku[0] && tahunBuku[0].id);
    }

    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Laporan Keuangan</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;">
        ${this._renderTabButton('buku-besar', 'Buku Besar')}
        ${this._renderTabButton('neraca-percobaan', 'Neraca Percobaan')}
        ${this._renderTabButton('rugi-laba', 'Rugi Laba')}
        ${this._renderTabButton('neraca', 'Neraca')}
        ${this._renderTabButton('perubahan-modal', 'Perubahan Modal')}
        ${this._renderTabButton('arus-kas', 'Arus Kas')}
      </div>
      <div class="panel">
        <div class="panel__header" style="display:flex; gap: var(--space-3); align-items:center; flex-wrap: wrap; justify-content: space-between;">
          <div style="display:flex; gap: var(--space-3); align-items:center; flex-wrap: wrap;">
            <label class="text-muted">Tahun Buku:
              <select id="filter-tahun-buku">
                ${tahunBuku.map(t => `<option value="${t.id}" ${t.id === this._tahunBukuId ? 'selected' : ''}>${t.tahun_buku} (${t.status})</option>`).join('')}
              </select>
            </label>
            ${this.tab === 'buku-besar' ? `
              <label class="text-muted">Akun:
                <select id="filter-akun"></select>
              </label>` : ''}
          </div>
          <button class="btn btn-outline btn-sm no-print" id="btn-cetak">🖨 Cetak / Export PDF</button>
        </div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;

    this.container.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => router.navigate(`laporan/${btn.dataset.tab}`));
    });
    this.container.querySelector('#btn-cetak').addEventListener('click', () => this._cetakLaporanAktif());

    const filterTahun = this.container.querySelector('#filter-tahun-buku');
    if (filterTahun) {
      filterTahun.addEventListener('change', () => {
        this._tahunBukuId = Number(filterTahun.value);
        this._pgBukuBesar.halaman = 1;
        this._muatData();
      });
    }

    if (this.tab === 'buku-besar') {
      const akun = await this._muatAkun();
      const filterAkun = this.container.querySelector('#filter-akun');
      filterAkun.innerHTML = akun.map(a => `<option value="${a.id}">${a.kode} - ${a.nama}</option>`).join('');
      if (!this._akunIdBukuBesar) this._akunIdBukuBesar = akun[0] && akun[0].id;
      filterAkun.value = this._akunIdBukuBesar;
      filterAkun.addEventListener('change', () => {
        this._akunIdBukuBesar = Number(filterAkun.value);
        this._pgBukuBesar.halaman = 1;
        this._muatData();
      });
    }

    await this._muatData();
  }

  _judulTab() {
    return {
      'buku-besar': 'Buku Besar',
      'neraca-percobaan': 'Neraca Percobaan',
      'rugi-laba': 'Rugi Laba',
      neraca: 'Neraca',
      'perubahan-modal': 'Perubahan Modal',
      'arus-kas': 'Arus Kas',
    }[this.tab];
  }

  _renderTabButton(key, label) {
    const active = this.tab === key ? 'btn-primary' : 'btn-outline';
    return `<button class="btn ${active} btn-sm" data-tab="${key}">${label}</button>`;
  }

  async _muatTahunBuku() {
    if (!this._tahunBukuCache) this._tahunBukuCache = await this.api.get('/referensi/tahun-buku');
    return this._tahunBukuCache;
  }

  async _muatAkun() {
    if (!this._akunCache) this._akunCache = await this.api.get('/referensi/akun');
    return this._akunCache;
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    if (!this._tahunBukuId) {
      target.innerHTML = '<div class="empty-state">Belum ada Tahun Buku. Buat dulu di modul Referensi.</div>';
      return;
    }
    try {
      if (this.tab === 'buku-besar') {
        if (!this._akunIdBukuBesar) { target.innerHTML = '<div class="empty-state">Belum ada akun.</div>'; return; }
        const qs = new URLSearchParams({
          akun_id: this._akunIdBukuBesar,
          tahun_buku_id: this._tahunBukuId,
          halaman: this._pgBukuBesar.halaman,
          ukuran_halaman: 20,
        });
        if (this._pgBukuBesar.cari) qs.set('cari', this._pgBukuBesar.cari);
        const hasil = await this.api.get(`/laporan/buku-besar?${qs.toString()}`);
        target.innerHTML = Pagination.renderControls({
          cari: this._pgBukuBesar.cari, halaman: hasil.halaman, total: hasil.total, ukuranHalaman: hasil.ukuran_halaman,
          searchPlaceholder: 'Cari no. jurnal / keterangan...',
        }) + TableRenderer.render([
          { key: 'tanggal', label: 'Tanggal' },
          { key: 'no_jurnal', label: 'No. Jurnal' },
          { key: 'keterangan', label: 'Keterangan' },
          { key: 'debit', label: 'Debit', type: 'uang' },
          { key: 'kredit', label: 'Kredit', type: 'uang' },
          { key: 'saldo', label: 'Saldo', type: 'uang' },
        ], hasil.items, { emptyMessage: 'Belum ada mutasi untuk akun & tahun buku ini.' });
        Pagination.attach(target, this._pgBukuBesar, () => this._muatData());
      } else if (this.tab === 'neraca-percobaan') {
        const data = await this.api.get(`/laporan/neraca-percobaan?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama Akun' },
          { key: 'kategori', label: 'Kategori' },
          { key: 'total_debit', label: 'Total Debit', type: 'uang' },
          { key: 'total_kredit', label: 'Total Kredit', type: 'uang' },
          { key: 'saldo', label: 'Saldo', type: 'uang' },
        ], data, { emptyMessage: 'Belum ada mutasi jurnal di tahun buku ini.' });
      } else if (this.tab === 'rugi-laba') {
        const rl = await this.api.get(`/laporan/rugi-laba?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = `
          <h3>Pendapatan</h3>
          ${TableRenderer.render([
            { key: 'kode', label: 'Kode' }, { key: 'nama', label: 'Nama' }, { key: 'saldo', label: 'Jumlah', type: 'uang' },
          ], rl.pendapatan, { emptyMessage: 'Belum ada pendapatan.' })}
          <p><strong>Total Pendapatan: ${TableRenderer.formatUang(rl.total_pendapatan)}</strong></p>
          <h3>Biaya</h3>
          ${TableRenderer.render([
            { key: 'kode', label: 'Kode' }, { key: 'nama', label: 'Nama' }, { key: 'saldo', label: 'Jumlah', type: 'uang' },
          ], rl.biaya, { emptyMessage: 'Belum ada biaya.' })}
          <p><strong>Total Biaya: ${TableRenderer.formatUang(rl.total_biaya)}</strong></p>
          <p><strong>Laba/Rugi: ${TableRenderer.formatUang(rl.laba_rugi)}</strong></p>
        `;
      } else if (this.tab === 'neraca') {
        const n = await this.api.get(`/laporan/neraca?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = `
          <h3>Aset</h3>
          ${TableRenderer.render([
            { key: 'kode', label: 'Kode' }, { key: 'nama', label: 'Nama' }, { key: 'saldo', label: 'Jumlah', type: 'uang' },
          ], n.aset, { emptyMessage: 'Belum ada aset.' })}
          <p><strong>Total Aset: ${TableRenderer.formatUang(n.total_aset)}</strong></p>
          <h3>Liabilitas</h3>
          ${TableRenderer.render([
            { key: 'kode', label: 'Kode' }, { key: 'nama', label: 'Nama' }, { key: 'saldo', label: 'Jumlah', type: 'uang' },
          ], n.liabilitas, { emptyMessage: 'Belum ada liabilitas.' })}
          <p><strong>Total Liabilitas: ${TableRenderer.formatUang(n.total_liabilitas)}</strong></p>
          <h3>Modal</h3>
          ${TableRenderer.render([
            { key: 'kode', label: 'Kode' }, { key: 'nama', label: 'Nama' }, { key: 'saldo', label: 'Jumlah', type: 'uang' },
          ], n.modal, { emptyMessage: 'Belum ada modal.' })}
          <p>Laba/Rugi periode berjalan (belum ditutup): ${TableRenderer.formatUang(n.laba_rugi_periode)}</p>
          <p><strong>Total Modal: ${TableRenderer.formatUang(n.total_modal)}</strong></p>
          <p class="badge badge--${n.balance ? 'success' : 'danger'}">${n.balance ? 'Neraca BALANCE' : 'Neraca TIDAK BALANCE'}</p>
        `;
      } else if (this.tab === 'perubahan-modal') {
        const pm = await this.api.get(`/laporan/perubahan-modal?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = `
          <table class="data-table">
            <tbody>
              <tr><td>Modal Awal</td><td class="uang">${TableRenderer.formatUang(pm.modal_awal)}</td></tr>
              <tr><td>Laba/Rugi Periode Berjalan</td><td class="uang">${TableRenderer.formatUang(pm.laba_rugi_periode)}</td></tr>
              <tr><td><strong>Modal Akhir</strong></td><td class="uang"><strong>${TableRenderer.formatUang(pm.modal_akhir)}</strong></td></tr>
            </tbody>
          </table>
        `;
      } else if (this.tab === 'arus-kas') {
        const ak = await this.api.get(`/laporan/arus-kas?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = `
          <p class="text-muted">Mutasi bersih akun-akun kategori Harta yang teridentifikasi sebagai kas (nama mengandung "Kas").</p>
          ${TableRenderer.render([
            { key: 'kode', label: 'Kode' }, { key: 'nama', label: 'Nama' },
            { key: 'kas_masuk', label: 'Kas Masuk', type: 'uang' },
            { key: 'kas_keluar', label: 'Kas Keluar', type: 'uang' },
            { key: 'mutasi_bersih', label: 'Mutasi Bersih', type: 'uang' },
          ], ak.akun, { emptyMessage: 'Belum ada akun kas teridentifikasi.' })}
          <p><strong>Total Mutasi Bersih: ${TableRenderer.formatUang(ak.total_mutasi_bersih)}</strong></p>
        `;
      }
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  _cetakLaporanAktif() {
    const tabContent = this.container.querySelector('#tab-content');
    const tanggalCetak = new Date().toLocaleDateString('id-ID');
    const titleHtml = `<h2>${this._judulTab()}</h2><p>Dicetak tanggal: ${tanggalCetak}</p>`;
    PrintHelper.cetak(titleHtml, tabContent.innerHTML);
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
