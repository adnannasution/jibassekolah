/**
 * Bootstrap aplikasi. Tiap kali ada modul baru selesai dibangun (Penerimaan,
 * Pengeluaran, dst), tinggal daftarkan di sini — satu baris, mengikuti pola
 * yang sudah ada untuk ReferensiModule.
 */
document.addEventListener('DOMContentLoaded', () => {
  const content = document.getElementById('main-content');
  const nav = document.getElementById('sidebar-nav');

  window.router = new Router(content, nav);

  router.register('referensi', ReferensiModule, 'Referensi', '📘');
  router.register('siswa', SiswaModule, 'Siswa & Calon Siswa', '🎓');
  // router.register('penerimaan', PenerimaanModule, 'Penerimaan', '💰');
  // router.register('pengeluaran', PengeluaranModule, 'Pengeluaran', '💸');
  // router.register('jurnal-umum', JurnalUmumModule, 'Jurnal Umum', '📝');
  // router.register('laporan', LaporanModule, 'Laporan Keuangan', '📊');
  // router.register('inventory', InventoryModule, 'Inventory', '📦');
  // router.register('pengaturan', PengaturanModule, 'Pengaturan', '⚙️');

  router.start('referensi');
});
