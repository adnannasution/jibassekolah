/**
 * Modul Dashboard — landing page ringkasan: saldo kas, siswa menunggak,
 * bar chart tunggakan per kelas (custom CSS, klik bar -> navigasi ke
 * LaporanPenerimaanModule tab siswa-menunggak dengan kelas_id terisi),
 * dan tabel transaksi terakhir.
 */
class DashboardModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this._tahunBukuCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Dashboard</div>
        <div class="page-title"><h1>Ringkasan</h1></div>
      </div>
      <div id="dashboard-body"><div class="empty-state">Memuat data...</div></div>
    `;
    await this._muatData();
  }

  async _muatTahunBuku() {
    if (!this._tahunBukuCache) this._tahunBukuCache = await this.api.get('/referensi/tahun-buku');
    return this._tahunBukuCache;
  }

  async _muatData() {
    const body = this.container.querySelector('#dashboard-body');
    try {
      const tahunBuku = await this._muatTahunBuku();
      const aktif = tahunBuku.find(t => t.status === 'AKTIF');
      if (!aktif) {
        body.innerHTML = '<div class="empty-state">Belum ada Tahun Buku aktif. Buat dulu di modul Referensi.</div>';
        return;
      }

      const ringkasan = await this.api.get(`/dashboard/ringkasan?tahun_buku_id=${aktif.id}`);

      body.innerHTML = `
        <div class="dashboard-cards">
          <div class="dashboard-card">
            <div class="dashboard-card__label">Saldo Kas</div>
            <div class="dashboard-card__value">${TableRenderer.formatUang(ringkasan.saldo_kas)}</div>
            <div class="dashboard-card__sub">Tahun Buku ${aktif.tahun_buku}</div>
          </div>
          <div class="dashboard-card">
            <div class="dashboard-card__label">Siswa Menunggak</div>
            <div class="dashboard-card__value">${ringkasan.jumlah_siswa_menunggak}</div>
            <div class="dashboard-card__sub">Total tunggakan: ${TableRenderer.formatUang(ringkasan.total_tunggakan)}</div>
          </div>
        </div>
        <div class="panel" style="margin-bottom: var(--space-5);">
          <div class="panel__header"><span class="text-muted">Tunggakan per Kelas</span></div>
          <div class="panel__body" id="bar-chart-container"></div>
        </div>
        <div class="panel">
          <div class="panel__header"><span class="text-muted">Transaksi Terakhir</span></div>
          <div class="panel__body" id="transaksi-terakhir-container"></div>
        </div>
      `;

      this._renderBarChart(ringkasan.tunggakan_per_kelas);

      const transaksiContainer = body.querySelector('#transaksi-terakhir-container');
      transaksiContainer.innerHTML = TableRenderer.render([
        { key: 'tanggal', label: 'Tanggal' },
        { key: 'no_jurnal', label: 'No. Jurnal' },
        { key: 'keterangan', label: 'Keterangan' },
        { key: 'sumber_modul', label: 'Sumber', type: 'badge', badgeMap: {
            PENERIMAAN: 'success', PENGELUARAN: 'danger', JURNAL_UMUM: 'neutral', TUTUP_BUKU: 'warning',
        } },
        { key: 'total', label: 'Total', type: 'uang' },
      ], ringkasan.transaksi_terakhir, { emptyMessage: 'Belum ada transaksi.' });
    } catch (err) {
      body.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  _renderBarChart(data) {
    const container = this.container.querySelector('#bar-chart-container');
    if (!data || data.length === 0) {
      container.innerHTML = '<div class="empty-state">Tidak ada tunggakan.</div>';
      return;
    }
    const maxSisa = Math.max(...data.map(d => Number(d.total_sisa)), 1);
    container.innerHTML = `
      <div class="bar-chart">
        ${data.map(d => {
          const persen = Math.max((Number(d.total_sisa) / maxSisa) * 100, 1);
          return `
            <div class="bar-chart__col" data-kelas-id="${d.kelas_id}" title="${d.kelas_nama}: ${TableRenderer.formatUang(d.total_sisa)}">
              <div class="bar-chart__bar" style="height: ${persen}%"></div>
              <div class="bar-chart__label">${d.kelas_nama}</div>
            </div>
          `;
        }).join('')}
      </div>
    `;
    container.querySelectorAll('.bar-chart__col').forEach(col => {
      col.addEventListener('click', () => {
        router.navigate(`laporan-penerimaan/siswa-menunggak/${col.dataset.kelasId}`);
      });
    });
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
