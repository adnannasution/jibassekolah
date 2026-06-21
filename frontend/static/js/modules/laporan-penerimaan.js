/**
 * Modul Laporan Penerimaan — laporan ~10 jenis dari sudut pandang siswa/kelas
 * (beda dari LaporanModule yang query jurnal_detail). Mengikuti pola tab
 * persis seperti ReferensiModule/LaporanModule.
 *
 * Tab siswa-menunggak baca params[1] sebagai kelas_id opsional (dipakai saat
 * navigasi dari Dashboard lewat klik bar chart: hash
 * #laporan-penerimaan/siswa-menunggak/<kelas_id> -> params[0]='siswa-menunggak',
 * params[1]='<kelas_id>').
 */
class LaporanPenerimaanModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'per-kelas'; // per-kelas | per-siswa | siswa-menunggak | rekapitulasi
    this._kelasIdAwal = this.tab === 'siswa-menunggak' && params[1] ? Number(params[1]) : null;
    this._departemenCache = null;
    this._tahunBukuCache = null;
    this._siswaCache = null;
    this._kelasCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Laporan Penerimaan</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;">
        ${this._renderTabButton('per-kelas', 'Per Kelas')}
        ${this._renderTabButton('per-siswa', 'Per Siswa')}
        ${this._renderTabButton('siswa-menunggak', 'Siswa Menunggak')}
        ${this._renderTabButton('rekapitulasi', 'Rekapitulasi')}
      </div>
      <div class="panel">
        <div class="panel__header">
          <div class="flex-between" style="gap: var(--space-3); flex: 1;">
            <span class="text-muted">Daftar ${this._judulTab()}</span>
            <div id="filter-container" style="display:flex; gap: var(--space-2);"></div>
          </div>
          <button class="btn btn-outline btn-sm no-print" id="btn-cetak">🖨 Cetak / Export PDF</button>
        </div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;

    this.container.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => router.navigate(`laporan-penerimaan/${btn.dataset.tab}`));
    });
    this.container.querySelector('#btn-cetak').addEventListener('click', () => this._cetakLaporanAktif());

    await this._renderFilter();
    await this._muatData();
  }

  _judulTab() {
    return {
      'per-kelas': 'Tagihan per Kelas',
      'per-siswa': 'Tagihan per Siswa',
      'siswa-menunggak': 'Siswa Menunggak',
      rekapitulasi: 'Rekapitulasi Penerimaan',
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

  async _muatTahunBuku() {
    if (!this._tahunBukuCache) this._tahunBukuCache = await this.api.get('/referensi/tahun-buku');
    return this._tahunBukuCache;
  }

  async _muatSiswa() {
    if (!this._siswaCache) this._siswaCache = await this.api.get('/siswa/siswa');
    return this._siswaCache;
  }

  async _muatKelas() {
    if (!this._kelasCache) this._kelasCache = await this.api.get('/siswa/kelas');
    return this._kelasCache;
  }

  _tahunBukuAktif(daftar) {
    return daftar.find(t => t.status === 'AKTIF');
  }

  async _renderFilter() {
    const filterEl = this.container.querySelector('#filter-container');
    const tahunBuku = await this._muatTahunBuku();
    const aktif = this._tahunBukuAktif(tahunBuku);
    if (!aktif) {
      filterEl.innerHTML = '';
      this._tahunBukuId = null;
      return;
    }
    this._tahunBukuId = aktif.id;

    let extraHtml = '';
    if (this.tab === 'per-siswa') {
      const siswa = await this._muatSiswa();
      extraHtml = `
        <select id="filter-siswa">
          <option value="">-- pilih siswa untuk detail --</option>
          ${siswa.map(s => `<option value="${s.id}">${s.nis} - ${s.nama}</option>`).join('')}
        </select>
      `;
    } else if (this.tab === 'siswa-menunggak') {
      const kelas = await this._muatKelas();
      extraHtml = `
        <select id="filter-kelas">
          <option value="">-- semua kelas --</option>
          ${kelas.map(k => `<option value="${k.id}" ${this._kelasIdAwal === k.id ? 'selected' : ''}>${k.nama}</option>`).join('')}
        </select>
      `;
    }

    filterEl.innerHTML = `<span class="text-muted">Tahun Buku: ${aktif.tahun_buku}</span>${extraHtml}`;

    const filterSiswa = filterEl.querySelector('#filter-siswa');
    if (filterSiswa) filterSiswa.addEventListener('change', () => this._muatData());
    const filterKelas = filterEl.querySelector('#filter-kelas');
    if (filterKelas) filterKelas.addEventListener('change', () => this._muatData());
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    if (!this._tahunBukuId) {
      target.innerHTML = '<div class="empty-state">Belum ada Tahun Buku aktif. Buat dulu di modul Referensi.</div>';
      return;
    }
    try {
      if (this.tab === 'per-kelas') {
        const data = await this.api.get(`/laporan-penerimaan/per-kelas?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = TableRenderer.render([
          { key: 'kelas_nama', label: 'Kelas' },
          { key: 'tingkat', label: 'Tingkat' },
          { key: 'total_tagihan', label: 'Total Tagihan', type: 'uang' },
          { key: 'total_diskon', label: 'Total Diskon', type: 'uang' },
          { key: 'total_sisa', label: 'Total Sisa', type: 'uang' },
          { key: 'jumlah_tagihan', label: 'Jumlah Tagihan' },
        ], data, { emptyMessage: 'Belum ada tagihan di tahun buku ini.', searchable: true, searchPlaceholder: 'Cari kelas...' });
        TableRenderer.attachSearch(target);
      } else if (this.tab === 'per-siswa') {
        const filterSiswa = this.container.querySelector('#filter-siswa');
        const siswaId = filterSiswa ? filterSiswa.value : '';
        if (siswaId) {
          const data = await this.api.get(`/laporan-penerimaan/per-siswa/${siswaId}?tahun_buku_id=${this._tahunBukuId}`);
          target.innerHTML = TableRenderer.render([
            { key: 'no_tagihan', label: 'No. Tagihan' },
            { key: 'tanggal', label: 'Tanggal' },
            { key: 'jenis_pembayaran_nama', label: 'Jenis Pembayaran' },
            { key: 'jumlah_tagihan', label: 'Jumlah', type: 'uang' },
            { key: 'diskon', label: 'Diskon', type: 'uang' },
            { key: 'sisa', label: 'Sisa', type: 'uang' },
            { key: 'status', label: 'Status', type: 'badge', badgeMap: {
                BELUM_LUNAS: 'warning', LUNAS: 'success', DIBATALKAN: 'danger',
            } },
          ], data, { emptyMessage: 'Siswa ini belum punya tagihan di tahun buku ini.' });
        } else {
          const data = await this.api.get(`/laporan-penerimaan/per-siswa?tahun_buku_id=${this._tahunBukuId}`);
          target.innerHTML = TableRenderer.render([
            { key: 'nis', label: 'NIS' },
            { key: 'nama', label: 'Nama' },
            { key: 'kelas_nama', label: 'Kelas' },
            { key: 'total_tagihan', label: 'Total Tagihan', type: 'uang' },
            { key: 'total_diskon', label: 'Total Diskon', type: 'uang' },
            { key: 'total_sisa', label: 'Total Sisa', type: 'uang' },
          ], data, { emptyMessage: 'Belum ada tagihan di tahun buku ini.', searchable: true, searchPlaceholder: 'Cari nama/NIS siswa...' });
          TableRenderer.attachSearch(target);
        }
      } else if (this.tab === 'siswa-menunggak') {
        const filterKelas = this.container.querySelector('#filter-kelas');
        const kelasId = filterKelas ? filterKelas.value : '';
        const qs = kelasId ? `&kelas_id=${kelasId}` : '';
        const data = await this.api.get(`/laporan-penerimaan/siswa-menunggak?tahun_buku_id=${this._tahunBukuId}${qs}`);
        target.innerHTML = TableRenderer.render([
          { key: 'no_tagihan', label: 'No. Tagihan' },
          { key: 'tanggal', label: 'Tanggal' },
          { key: 'siswa_nis', label: 'NIS' },
          { key: 'siswa_nama', label: 'Nama Siswa' },
          { key: 'kelas_nama', label: 'Kelas' },
          { key: 'jenis_pembayaran_nama', label: 'Jenis Pembayaran' },
          { key: 'sisa', label: 'Sisa', type: 'uang' },
        ], data, { emptyMessage: 'Tidak ada siswa menunggak.', searchable: true, searchPlaceholder: 'Cari nama/NIS siswa...' });
        TableRenderer.attachSearch(target);
      } else if (this.tab === 'rekapitulasi') {
        const data = await this.api.get(`/laporan-penerimaan/rekapitulasi?tahun_buku_id=${this._tahunBukuId}`);
        target.innerHTML = TableRenderer.render([
          { key: 'jenis_pembayaran_nama', label: 'Jenis Pembayaran' },
          { key: 'total_ditagihkan', label: 'Total Ditagihkan', type: 'uang' },
          { key: 'total_diterima', label: 'Total Diterima', type: 'uang' },
        ], data, { emptyMessage: 'Belum ada data penerimaan di tahun buku ini.' });
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
