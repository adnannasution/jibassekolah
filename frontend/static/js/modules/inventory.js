/**
 * Modul Inventory — Group Barang (hierarkis) & Data Barang. Modul ini murni
 * master data stok barang, TIDAK menyentuh jurnal/ledger sama sekali
 * (lihat CLAUDE.md roadmap modul 7).
 */
class InventoryModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this.tab = params[0] || 'group-barang'; // group-barang | barang
    this._groupCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Inventory</div>
        <div class="page-title"><h1>${this._judulTab()}</h1></div>
      </div>
      <div class="tabs" style="display:flex; gap: var(--space-2); margin-bottom: var(--space-4);">
        ${this._renderTabButton('group-barang', 'Group Barang')}
        ${this._renderTabButton('barang', 'Data Barang')}
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
      btn.addEventListener('click', () => router.navigate(`inventory/${btn.dataset.tab}`));
    });
    this.container.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());

    await this._muatData();
  }

  _judulTab() {
    return { 'group-barang': 'Group Barang', barang: 'Data Barang' }[this.tab];
  }

  _renderTabButton(key, label) {
    const active = this.tab === key ? 'btn-primary' : 'btn-outline';
    return `<button class="btn ${active} btn-sm" data-tab="${key}">${label}</button>`;
  }

  async _muatGroup() {
    if (!this._groupCache) this._groupCache = await this.api.get('/inventory/group-barang');
    return this._groupCache;
  }

  _namaGroupBerjenjang(group, semuaGroup) {
    const jejak = [group.nama];
    let cursor = group;
    while (cursor.parent_id) {
      cursor = semuaGroup.find(g => g.id === cursor.parent_id);
      if (!cursor) break;
      jejak.unshift(cursor.nama);
    }
    return jejak.join(' > ');
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    try {
      if (this.tab === 'group-barang') {
        const data = await this.api.get('/inventory/group-barang');
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama Group', render: (row) => this._namaGroupBerjenjang(row, data) },
          { key: 'aktif', label: 'Status', type: 'badge', badgeMap: { true: 'success', false: 'neutral' } },
        ], data, { emptyMessage: 'Belum ada group barang.' });
      } else if (this.tab === 'barang') {
        const [data, group] = await Promise.all([this.api.get('/inventory/barang'), this._muatGroup()]);
        target.innerHTML = TableRenderer.render([
          { key: 'kode', label: 'Kode' },
          { key: 'nama', label: 'Nama Barang' },
          { key: 'group_id', label: 'Group', render: (row) => {
              const g = group.find(x => x.id === row.group_id);
              return g ? this._namaGroupBerjenjang(g, group) : '-';
          } },
          { key: 'satuan', label: 'Satuan' },
          { key: 'stok', label: 'Stok' },
          { key: 'harga_satuan', label: 'Harga Satuan', type: 'uang' },
          { key: 'aktif', label: 'Status', type: 'badge', badgeMap: { true: 'success', false: 'neutral' } },
        ], data, { emptyMessage: 'Belum ada data barang. Tambahkan dulu group-nya.' });
      }
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  async _bukaFormTambah() {
    if (this.tab === 'group-barang') {
      const group = await this._muatGroup();
      Modal.open({
        title: 'Tambah Group Barang',
        bodyHtml: FormBuilder.render([
          { name: 'kode', label: 'Kode (mis. ELK-KOM)', required: true },
          { name: 'nama', label: 'Nama Group', required: true },
          { name: 'parent_id', label: 'Group Induk (opsional)', type: 'select',
            options: [{ value: '', label: '— Tidak ada (group utama) —' }]
              .concat(group.map(g => ({ value: g.id, label: this._namaGroupBerjenjang(g, group) }))) },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/inventory/group-barang', {
            kode: data.kode,
            nama: data.nama,
            parent_id: data.parent_id ? Number(data.parent_id) : null,
            aktif: true,
          });
          this._groupCache = null;
          close();
          this._muatData();
        },
      });
    } else if (this.tab === 'barang') {
      const group = await this._muatGroup();
      if (!group.length) {
        window.alert('Belum ada group barang. Tambahkan dulu di tab Group Barang.');
        return;
      }
      Modal.open({
        title: 'Tambah Data Barang',
        bodyHtml: FormBuilder.render([
          { name: 'group_id', label: 'Group Barang', type: 'select', required: true,
            options: group.map(g => ({ value: g.id, label: this._namaGroupBerjenjang(g, group) })) },
          { name: 'kode', label: 'Kode Barang', required: true },
          { name: 'nama', label: 'Nama Barang', required: true },
          { name: 'satuan', label: 'Satuan (mis. unit, box, pcs)', required: true },
          { name: 'stok', label: 'Stok Awal', type: 'number', required: true },
          { name: 'harga_satuan', label: 'Harga Satuan', type: 'uang' },
          { name: 'keterangan', label: 'Keterangan', type: 'textarea' },
        ]),
        onSubmit: async (data, close) => {
          await this.api.post('/inventory/barang', {
            group_id: Number(data.group_id),
            kode: data.kode,
            nama: data.nama,
            satuan: data.satuan,
            stok: data.stok || 0,
            harga_satuan: data.harga_satuan || null,
            keterangan: data.keterangan || null,
            aktif: true,
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
