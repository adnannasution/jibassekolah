/**
 * Bootstrap aplikasi. Tiap kali ada modul baru selesai dibangun (Penerimaan,
 * Pengeluaran, dst), tinggal daftarkan di sini — satu baris, mengikuti pola
 * yang sudah ada untuk ReferensiModule.
 */
document.addEventListener('DOMContentLoaded', () => {
  Theme.terapkan();

  const content = document.getElementById('main-content');
  const nav = document.getElementById('sidebar-nav');

  if (!Auth.getUser()) {
    _renderLoginScreen(content);
    return;
  }

  _mulaiApp(content, nav);
});

function _renderLoginScreen(content) {
  content.innerHTML = `
    <div class="panel" style="max-width: 360px; margin: var(--space-8) auto;">
      <div class="panel__header"><span>Login Brilliant Finance</span></div>
      <div class="panel__body">
        ${FormBuilder.render([
          { name: 'login', label: 'Login', required: true },
          { name: 'password', label: 'Password', type: 'password', required: true },
        ])}
        <div id="login-error" class="text-muted" style="color: var(--color-danger, #b00020); display:none;"></div>
        <button class="btn btn-primary" id="btn-login" style="margin-top: var(--space-3);">Masuk</button>
      </div>
    </div>
  `;
  content.querySelector('#btn-login').addEventListener('click', async () => {
    const login = content.querySelector('#f_login').value;
    const password = content.querySelector('#f_password').value;
    const errorEl = content.querySelector('#login-error');
    try {
      const hasil = await api.post('/pengaturan/login', { login, password });
      Auth.setUser(hasil.user);
      window.location.reload();
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    }
  });
}

function _mulaiApp(content, nav) {
  window.router = new Router(content, nav);

  router.register('dashboard', DashboardModule, 'Dashboard', '🏠');
  router.register('referensi', ReferensiModule, 'Referensi', '📘');
  router.register('siswa', SiswaModule, 'Siswa & Calon Siswa', '🎓');
  router.register('penerimaan', PenerimaanModule, 'Penerimaan', '💰');
  router.register('pengeluaran', PengeluaranModule, 'Pengeluaran', '💸');
  router.register('jurnal-umum', JurnalUmumModule, 'Jurnal Umum', '📝');
  router.register('laporan', LaporanModule, 'Laporan Keuangan', '📊');
  router.register('laporan-penerimaan', LaporanPenerimaanModule, 'Laporan Penerimaan', '📈');
  router.register('inventory', InventoryModule, 'Inventory', '📦');
  router.register('pengaturan', PengaturanModule, 'Pengaturan', '⚙️');

  const user = Auth.getUser();
  const footer = document.getElementById('sidebar-footer');
  footer.innerHTML = `
    <div>${user.nama} (${user.tingkat})</div>
    <button class="btn btn-outline btn-sm" id="btn-logout" style="margin-top: var(--space-2);">Keluar</button>
  `;
  footer.querySelector('#btn-logout').addEventListener('click', () => {
    Auth.logout();
    window.location.reload();
  });

  router.start('dashboard');
}
