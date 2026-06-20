/**
 * Modul Siswa & Calon Siswa — Kelas, Siswa, Kelompok Calon Siswa, Calon Siswa.
 * Mengikuti pola yang sama dengan ReferensiModule (constructor, render(), destroy()).
 */
class SiswaModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'kelas'; // kelas | siswa | kelompok-calon-siswa | calon-siswa
    this._departemenCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Siswa &amp; Calon Siswa</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap;">
        ${this._renderTabButton('kelas', 'Kelas')}
        ${this._renderTabButton('siswa', 'Siswa')}
        ${this._renderTabButton('kelompok-calon-siswa', 'Kelompok Calon Siswa')}
        ${this._renderTabButton('calon-siswa', 'Calon Siswa')}
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
      btn.addEventListener('click', () => router.navigate(`siswa/${btn.dataset.tab}`));
    });
    this.container.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());

    await this._muatData();
  }

  _judulTab() {
    return {
      kelas: 'Kelas',
      siswa: 'Siswa',
      'kelompok-calon-siswa': 'Kelompok Calon Siswa',
      'calon-siswa': 'Calon Siswa',
    }[this.tab];
  }

  _renderTabButton(key, label) {
    const active = this.tab === key ? 'btn-primary' : 'btn-outline';
    return `<button class="btn ${active} btn-sm" data-tab="${key}">${label}</button>`;
  }

  async _muatDepartemen() {
    if (!this._departemenCache) {
      this._departemenCache = await this.api.get('/referensi/departemen');
    }
    return this._departemenCache;
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    try {
      if (this.tab === 'kelas') {
        const data = await this.api.get('/siswa/kelas');
        target.innerHTML = TableRenderer.render([
          { key: 'angkatan', label: 'Angkatan' },
          { key: 'tingkat', label: 'Tingkat' },
          { key: 'nama', label: 'Nama Kelas' },
        ], data, { emptyMessage: 'Belum ada kelas. Tambahkan dulu (mis. 1-A, XI IPA 1).' });
      } else if (this.tab === 'siswa') {
        const data = await this.api.get('/siswa/siswa');
        target.innerHTML = TableRenderer.render([
          { key: 'nis', label: 'NIS' },
          { key: 'nama', label: 'Nama' },
          { key: 'hp', label: 'No. HP' },
          { key: 'status', label: 'Status', type: 'badge', badgeMap: {
              AKTIF: 'success', LULUS: 'neutral', KELUAR: 'danger',
          } },
        ], data, { emptyMessage: 'Belum ada siswa terdaftar.' });
      } else if (this.tab === 'kelompok-calon-siswa') {
        const data = await this.api.get('/siswa/kelompok-calon-siswa');
        target.innerHTML = TableRenderer.render([
          { key: 'nama', label: 'Nama Kelompok' },
        ], data, { emptyMessage: 'Belum ada kelompok calon siswa (mis. Jalur PMDK, NON-PMDK).' });
      } else if (this.tab === 'calon-siswa') {
        const data = await this.api.get('/siswa/calon-siswa');
        target.innerHTML = TableRenderer.render([
          { key: 'no_registrasi', label: 'No. Registrasi' },
          { key: 'nama', label: 'Nama' },
          { key: 'proses', label: 'Proses' },
          { key: 'hp', label: 'No. HP' },
          { key: 'tanggal_daftar', label: 'Tanggal Daftar' },
        ], data, { emptyMessage: 'Belum ada calon siswa terdaftar.' });
      }
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  async _bukaFormTambah() {
    const departemen = await this._muatDepartemen();
    const departemenOptions = departemen.map(d => ({ value: d.id, label: d.nama }));

    if (this.tab === 'kelas') {
      Modal.open({
        title: 'Tambah Kelas',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'angkatan', label: 'Angkatan (mis. 2025)', required: true },
          { name: 'tingkat', label: 'Tingkat (mis. X, XI, 1, 2)', required: true },
          { name: 'nama', label: 'Nama Kelas (mis. XI IPA 1)', required: true },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/siswa/kelas', { ...data, departemen_id: Number(data.departemen_id) });
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'siswa') {
      const kelas = await this.api.get('/siswa/kelas');
      if (!kelas.length) {
        window.alert('Belum ada Kelas. Tambahkan dulu di tab Kelas.');
        return;
      }
      Modal.open({
        title: 'Tambah Siswa',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'kelas_id', label: 'Kelas', type: 'select', required: true,
            options: kelas.map(k => ({ value: k.id, label: k.nama })) },
          { name: 'nis', label: 'NIS', required: true },
          { name: 'nama', label: 'Nama Siswa', required: true },
          { name: 'hp', label: 'No. HP' },
          { name: 'telepon', label: 'Telepon' },
          { name: 'alamat', label: 'Alamat', type: 'textarea' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/siswa/siswa', {
            ...data,
            departemen_id: Number(data.departemen_id),
            kelas_id: Number(data.kelas_id),
          });
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'kelompok-calon-siswa') {
      Modal.open({
        title: 'Tambah Kelompok Calon Siswa',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'nama', label: 'Nama Kelompok (mis. Jalur PMDK)', required: true },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/siswa/kelompok-calon-siswa', { ...data, departemen_id: Number(data.departemen_id) });
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'calon-siswa') {
      const kelompok = await this.api.get('/siswa/kelompok-calon-siswa');
      if (!kelompok.length) {
        window.alert('Belum ada Kelompok Calon Siswa. Tambahkan dulu di tab Kelompok Calon Siswa.');
        return;
      }
      Modal.open({
        title: 'Tambah Calon Siswa',
        bodyHtml: FormBuilder.render([
          { name: 'departemen_id', label: 'Departemen', type: 'select', required: true, options: departemenOptions },
          { name: 'kelompok_id', label: 'Kelompok', type: 'select', required: true,
            options: kelompok.map(k => ({ value: k.id, label: k.nama })) },
          { name: 'no_registrasi', label: 'No. Registrasi', required: true },
          { name: 'nama', label: 'Nama Calon Siswa', required: true },
          { name: 'proses', label: 'Proses (mis. Pendaftaran (A))' },
          { name: 'hp', label: 'No. HP' },
          { name: 'alamat', label: 'Alamat', type: 'textarea' },
          { name: 'tanggal_daftar', label: 'Tanggal Daftar', type: 'date' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/siswa/calon-siswa', {
            ...data,
            departemen_id: Number(data.departemen_id),
            kelompok_id: Number(data.kelompok_id),
            tanggal_daftar: data.tanggal_daftar || null,
          });
          close();
          this._muatData();
        },
      });
    }
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
