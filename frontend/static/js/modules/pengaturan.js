/**
 * Modul Pengaturan — manajemen user & role (admin/manajer/staf), scoped per
 * departemen. Modul terakhir di roadmap (lihat CLAUDE.md). Belum ada
 * session/token penuh, login di sini cuma menyimpan user aktif di
 * localStorage lewat Auth, dipakai modul lain pengganti placeholder
 * petugas_id=1/user_id=1.
 */
class PengaturanModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
  }

  async render() {
    const [users, departemen] = await Promise.all([
      this.api.get('/pengaturan/users'),
      this.api.get('/referensi/departemen'),
    ]);
    this._departemenCache = departemen;

    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Pengaturan</div>
        <div class="page-title"><h1>Pengguna & Role</h1></div>
      </div>
      <div class="panel">
        <div class="panel__header">
          <span class="text-muted">Daftar Pengguna</span>
          <button class="btn btn-primary btn-sm" id="btn-tambah">+ Tambah Pengguna</button>
        </div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;

    this.container.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());
    this._renderTabel(users);
  }

  _namaDepartemen(id) {
    if (!id) return 'Semua Departemen';
    const d = this._departemenCache.find(x => x.id === id);
    return d ? d.nama : '-';
  }

  _renderTabel(users) {
    const target = this.container.querySelector('#tab-content');
    target.innerHTML = TableRenderer.render([
      { key: 'login', label: 'Login' },
      { key: 'nama', label: 'Nama' },
      { key: 'tingkat', label: 'Tingkat', type: 'badge', badgeMap: { ADMIN: 'success', MANAJER: 'warning', STAF: 'neutral' } },
      { key: 'departemen_id', label: 'Departemen', render: (row) => this._namaDepartemen(row.departemen_id) },
      { key: 'aktif', label: 'Status', type: 'badge', badgeMap: { true: 'success', false: 'neutral' } },
      { key: 'aksi', label: '', type: 'aksi', render: (row) => `
          <button class="btn btn-outline btn-sm" data-ganti-password="${row.id}">Ganti Password</button>
          <button class="btn btn-outline btn-sm" data-toggle-aktif="${row.id}">${row.aktif ? 'Nonaktifkan' : 'Aktifkan'}</button>
      ` },
    ], users, { emptyMessage: 'Belum ada pengguna.' });

    target.querySelectorAll('[data-ganti-password]').forEach(btn => {
      btn.addEventListener('click', () => this._bukaFormGantiPassword(Number(btn.dataset.gantiPassword)));
    });
    target.querySelectorAll('[data-toggle-aktif]').forEach(btn => {
      btn.addEventListener('click', () => this._toggleAktif(users.find(u => u.id === Number(btn.dataset.toggleAktif))));
    });
  }

  async _muatUlang() {
    const users = await this.api.get('/pengaturan/users');
    this._renderTabel(users);
  }

  _bukaFormTambah() {
    Modal.open({
      title: 'Tambah Pengguna',
      bodyHtml: FormBuilder.render([
        { name: 'login', label: 'Login', required: true },
        { name: 'nama', label: 'Nama', required: true },
        { name: 'password', label: 'Password', type: 'password', required: true },
        { name: 'tingkat', label: 'Tingkat', type: 'select', required: true, options: [
          { value: 'ADMIN', label: 'Admin' }, { value: 'MANAJER', label: 'Manajer' }, { value: 'STAF', label: 'Staf' },
        ] },
        { name: 'departemen_id', label: 'Departemen (kosongkan = semua departemen)', type: 'select',
          options: [{ value: '', label: '— Semua Departemen —' }]
            .concat(this._departemenCache.map(d => ({ value: d.id, label: d.nama }))) },
      ]),
      onSubmit: async (data, close) => {
        await this.api.post('/pengaturan/users', {
          login: data.login,
          nama: data.nama,
          password: data.password,
          tingkat: data.tingkat,
          departemen_id: data.departemen_id ? Number(data.departemen_id) : null,
        });
        close();
        this._muatUlang();
      },
    });
  }

  _bukaFormGantiPassword(userId) {
    Modal.open({
      title: 'Ganti Password',
      bodyHtml: FormBuilder.render([
        { name: 'password_baru', label: 'Password Baru', type: 'password', required: true },
      ]),
      onSubmit: async (data, close) => {
        await this.api.post(`/pengaturan/users/${userId}/ganti-password`, { password_baru: data.password_baru });
        close();
        Modal.alert('Password berhasil diganti.');
      },
    });
  }

  async _toggleAktif(user) {
    await this.api.put(`/pengaturan/users/${user.id}`, { aktif: !user.aktif });
    this._muatUlang();
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
