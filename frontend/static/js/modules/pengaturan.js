/**
 * Modul Pengaturan — manajemen user & role (admin/manajer/staf), scoped per
 * departemen, plus Log Aktivitas Pengguna (siapa melakukan apa, lewat
 * audit_log generik yang juga dipakai modul Laporan Keuangan). Belum ada
 * session/token penuh, login di sini cuma menyimpan user aktif di
 * localStorage lewat Auth, dipakai modul lain pengganti placeholder
 * petugas_id=1/user_id=1.
 */
const LABEL_TABEL_AUDIT = {
  jurnal_header: 'Jurnal Umum',
  tagihan: 'Tagihan',
  pembayaran_tagihan: 'Pembayaran Tagihan',
  pengeluaran: 'Pengeluaran',
  users: 'Pengguna',
};

class PengaturanModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'pengguna';
    this._pgLogAktivitas = { cari: '', halaman: 1 };
    this._filterTabel = '';
    this._filterAksi = '';
  }

  async render() {
    const departemen = await this.api.get('/referensi/departemen');
    this._departemenCache = departemen;

    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Pengaturan</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;">
        ${this._renderTabButton('pengguna', 'Pengguna & Role')}
        ${this._renderTabButton('log-aktivitas', 'Log Aktivitas')}
      </div>
      <div class="panel">
        <div class="panel__header" id="panel-header"></div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;

    this.container.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => router.navigate(`pengaturan/${btn.dataset.tab}`));
    });

    await this._muatData();
  }

  _judulTab() {
    return { pengguna: 'Pengguna & Role', 'log-aktivitas': 'Log Aktivitas' }[this.tab];
  }

  _renderTabButton(key, label) {
    const active = this.tab === key ? 'btn-primary' : 'btn-outline';
    return `<button class="btn ${active} btn-sm" data-tab="${key}">${label}</button>`;
  }

  async _muatData() {
    if (this.tab === 'pengguna') {
      await this._muatPengguna();
    } else if (this.tab === 'log-aktivitas') {
      await this._muatLogAktivitas();
    }
  }

  // ===== Tab: Pengguna & Role =====

  async _muatPengguna() {
    const header = this.container.querySelector('#panel-header');
    header.innerHTML = `
      <span class="text-muted">Daftar Pengguna</span>
      <button class="btn btn-primary btn-sm" id="btn-tambah">+ Tambah Pengguna</button>
    `;
    header.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());

    const users = await this.api.get('/pengaturan/users');
    this._renderTabelPengguna(users);
  }

  _namaDepartemen(id) {
    if (!id) return 'Semua Departemen';
    const d = this._departemenCache.find(x => x.id === id);
    return d ? d.nama : '-';
  }

  _renderTabelPengguna(users) {
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

  async _muatUlangPengguna() {
    const users = await this.api.get('/pengaturan/users');
    this._renderTabelPengguna(users);
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
        await this.api.post(`/pengaturan/users?pelaku_id=${Auth.userId()}`, {
          login: data.login,
          nama: data.nama,
          password: data.password,
          tingkat: data.tingkat,
          departemen_id: data.departemen_id ? Number(data.departemen_id) : null,
        });
        close();
        this._muatUlangPengguna();
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
        await this.api.post(`/pengaturan/users/${userId}/ganti-password?pelaku_id=${Auth.userId()}`, { password_baru: data.password_baru });
        close();
        Modal.alert('Password berhasil diganti.');
      },
    });
  }

  async _toggleAktif(user) {
    await this.api.put(`/pengaturan/users/${user.id}?pelaku_id=${Auth.userId()}`, { aktif: !user.aktif });
    this._muatUlangPengguna();
  }

  // ===== Tab: Log Aktivitas =====

  async _muatLogAktivitas() {
    const header = this.container.querySelector('#panel-header');
    header.innerHTML = `
      <div style="display:flex; gap: var(--space-3); align-items:center; flex-wrap: wrap;">
        <label class="text-muted">Tabel:
          <select id="filter-tabel-audit">
            <option value="">Semua</option>
            ${Object.entries(LABEL_TABEL_AUDIT).map(([key, label]) => `<option value="${key}" ${this._filterTabel === key ? 'selected' : ''}>${label}</option>`).join('')}
          </select>
        </label>
        <label class="text-muted">Aksi:
          <select id="filter-aksi-audit">
            <option value="">Semua</option>
            <option value="BUAT" ${this._filterAksi === 'BUAT' ? 'selected' : ''}>Buat</option>
            <option value="EDIT" ${this._filterAksi === 'EDIT' ? 'selected' : ''}>Edit</option>
            <option value="HAPUS" ${this._filterAksi === 'HAPUS' ? 'selected' : ''}>Hapus</option>
            <option value="LOGIN" ${this._filterAksi === 'LOGIN' ? 'selected' : ''}>Login</option>
          </select>
        </label>
      </div>
    `;
    header.querySelector('#filter-tabel-audit').addEventListener('change', (e) => {
      this._filterTabel = e.target.value;
      this._pgLogAktivitas.halaman = 1;
      this._muatLogAktivitas();
    });
    header.querySelector('#filter-aksi-audit').addEventListener('change', (e) => {
      this._filterAksi = e.target.value;
      this._pgLogAktivitas.halaman = 1;
      this._muatLogAktivitas();
    });

    const target = this.container.querySelector('#tab-content');
    try {
      const qs = new URLSearchParams({ halaman: this._pgLogAktivitas.halaman, ukuran_halaman: 20 });
      if (this._pgLogAktivitas.cari) qs.set('cari', this._pgLogAktivitas.cari);
      if (this._filterTabel) qs.set('tabel', this._filterTabel);
      if (this._filterAksi) qs.set('aksi', this._filterAksi);
      const hasil = await this.api.get(`/laporan/audit-log?${qs.toString()}`);
      target.innerHTML = Pagination.renderControls({
        cari: this._pgLogAktivitas.cari, halaman: hasil.halaman, total: hasil.total, ukuranHalaman: hasil.ukuran_halaman,
        searchPlaceholder: 'Cari tabel / alasan...',
      }) + TableRenderer.render([
        { key: 'created_at', label: 'Waktu' },
        { key: 'user_nama', label: 'Pengguna', render: (row) => `${row.user_nama || '-'}${row.user_login ? ` (${row.user_login})` : ''}` },
        { key: 'tabel', label: 'Tabel', render: (row) => LABEL_TABEL_AUDIT[row.tabel] || row.tabel },
        { key: 'aksi', label: 'Aksi', type: 'badge', badgeMap: { BUAT: 'success', EDIT: 'warning', HAPUS: 'danger', LOGIN: 'neutral' } },
        { key: 'alasan', label: 'Alasan', render: (row) => row.alasan || '-' },
        { key: 'aksi_detail', label: '', type: 'aksi', render: (row) => (row.data_lama || row.data_baru)
          ? `<button class="btn btn-outline btn-sm" data-lihat-detail="${row.id}">Lihat Detail</button>` : '' },
      ], hasil.items, { emptyMessage: 'Belum ada aktivitas yang tercatat.' });
      Pagination.attach(target, this._pgLogAktivitas, () => this._muatLogAktivitas());

      target.querySelectorAll('[data-lihat-detail]').forEach(btn => {
        btn.addEventListener('click', () => {
          const row = hasil.items.find(r => r.id === Number(btn.dataset.lihatDetail));
          this._bukaDetailAudit(row);
        });
      });
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  _bukaDetailAudit(row) {
    Modal.open({
      title: `Detail Aktivitas — ${LABEL_TABEL_AUDIT[row.tabel] || row.tabel} #${row.record_id}`,
      size: 'lg',
      submitLabel: 'Tutup',
      bodyHtml: `
        <div style="display:flex; gap: var(--space-4); flex-wrap: wrap;">
          <div style="flex:1; min-width: 200px;">
            <strong>Data Lama</strong>
            <pre style="white-space:pre-wrap; background: var(--color-bg-muted, #f5f5f5); padding: var(--space-2); border-radius: var(--radius-sm);">${row.data_lama ? JSON.stringify(row.data_lama, null, 2) : '-'}</pre>
          </div>
          <div style="flex:1; min-width: 200px;">
            <strong>Data Baru</strong>
            <pre style="white-space:pre-wrap; background: var(--color-bg-muted, #f5f5f5); padding: var(--space-2); border-radius: var(--radius-sm);">${row.data_baru ? JSON.stringify(row.data_baru, null, 2) : '-'}</pre>
          </div>
        </div>
      `,
      onSubmit: async (_, close) => close(),
    });
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
