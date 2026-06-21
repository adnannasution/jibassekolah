/**
 * Modul Jurnal Umum — input manual baris debit/kredit (jumlah baris bebas,
 * tambah/hapus dinamis) + validasi balance real-time sebelum submit.
 * Posting tetap lewat satu pintu jurnal (app/core/ledger.py::posting_jurnal()),
 * modul ini cuma UI untuk transaksi yang tidak masuk kategori Penerimaan/Pengeluaran.
 */
class JurnalUmumModule {
  constructor(container, api, params) {
    this.container = container;
    this.api = api;
    this._departemenCache = null;
    this._akunCache = null;
    this._tahunBukuCache = null;
  }

  async render() {
    this.container.innerHTML = `
      <div class="page-header">
        <div class="breadcrumb">Jurnal Umum</div>
        <div class="page-title"><h1>Jurnal Umum</h1></div>
      </div>
      <div class="panel">
        <div class="panel__header">
          <span class="text-muted">Daftar Jurnal Umum (input manual)</span>
          <button class="btn btn-primary btn-sm" id="btn-tambah">+ Tambah Jurnal</button>
        </div>
        <div class="panel__body" id="tab-content">
          <div class="empty-state">Memuat data...</div>
        </div>
      </div>
    `;
    this.container.querySelector('#btn-tambah').addEventListener('click', () => this._bukaFormTambah());
    await this._muatData();
  }

  async _muatDepartemen() {
    if (!this._departemenCache) this._departemenCache = await this.api.get('/referensi/departemen');
    return this._departemenCache;
  }

  async _muatAkun() {
    if (!this._akunCache) this._akunCache = await this.api.get('/referensi/akun');
    return this._akunCache;
  }

  async _muatTahunBuku() {
    if (!this._tahunBukuCache) this._tahunBukuCache = await this.api.get('/referensi/tahun-buku');
    return this._tahunBukuCache;
  }

  _tahunBukuAktif(daftar) {
    return daftar.find(t => t.status === 'AKTIF');
  }

  async _muatData() {
    const target = this.container.querySelector('#tab-content');
    try {
      const data = await this.api.get('/jurnal-umum/jurnal?sumber_modul=JURNAL_UMUM');
      target.innerHTML = TableRenderer.render([
        { key: 'no_jurnal', label: 'No. Jurnal' },
        { key: 'tanggal', label: 'Tanggal' },
        { key: 'keterangan', label: 'Keterangan' },
        { key: 'total', label: 'Total', render: (row) =>
            TableRenderer.formatUang(row.detail.reduce((s, d) => s + Number(d.debit), 0)) },
        { key: 'status', label: 'Status', type: 'badge', badgeMap: { AKTIF: 'success', DIBATALKAN: 'danger' } },
        { key: 'aksi', label: '', type: 'aksi', render: (row) => row.status === 'AKTIF'
            ? `<button class="btn btn-outline btn-sm" data-batal="${row.id}">Batalkan</button>`
            : '' },
      ], data, { emptyMessage: 'Belum ada jurnal umum. Tambahkan dulu lewat tombol + Tambah Jurnal.' });

      target.querySelectorAll('[data-batal]').forEach(btn => {
        btn.addEventListener('click', () => this._batalkanJurnal(Number(btn.dataset.batal)));
      });
    } catch (err) {
      target.innerHTML = `<div class="empty-state">Gagal memuat data: ${err.message}</div>`;
    }
  }

  _barisHtml(akunOptionsHtml) {
    return `
      <div class="jurnal-baris" style="display:flex; gap:var(--space-2); margin-bottom:var(--space-2); align-items:center;">
        <select class="jb-akun" style="flex:2;">
          <option value="">-- pilih akun --</option>
          ${akunOptionsHtml}
        </select>
        <input type="number" step="0.01" class="jb-debit" placeholder="Debit" style="flex:1;" />
        <input type="number" step="0.01" class="jb-kredit" placeholder="Kredit" style="flex:1;" />
        <button type="button" class="btn btn-outline btn-sm jb-hapus">&times;</button>
      </div>`;
  }

  async _bukaFormTambah() {
    const [departemen, akun, tahunBuku] = await Promise.all([
      this._muatDepartemen(), this._muatAkun(), this._muatTahunBuku(),
    ]);
    const aktif = this._tahunBukuAktif(tahunBuku);
    if (!aktif) {
      window.alert('Belum ada Tahun Buku aktif. Buat dulu di modul Referensi.');
      return;
    }
    const akunOptionsHtml = akun.map(a => `<option value="${a.id}">${a.kode} - ${a.nama}</option>`).join('');

    Modal.open({
      title: 'Tambah Jurnal Umum',
      bodyHtml: `
        <div class="form-group">
          <label for="ju-departemen">Departemen</label>
          <select id="ju-departemen" required>
            ${departemen.map(d => `<option value="${d.id}">${d.nama}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label for="ju-tanggal">Tanggal</label>
          <input id="ju-tanggal" type="date" required />
        </div>
        <div class="form-group">
          <label for="ju-keterangan">Keterangan</label>
          <textarea id="ju-keterangan" required></textarea>
        </div>
        <div id="ju-baris-container">
          ${this._barisHtml(akunOptionsHtml)}
          ${this._barisHtml(akunOptionsHtml)}
        </div>
        <button type="button" id="ju-tambah-baris" class="btn btn-outline btn-sm">+ Tambah Baris</button>
        <div id="ju-balance-info" class="text-muted" style="margin-top: var(--space-2);"></div>
      `,
      onSubmit: async (_data, close) => {
        const overlay = document.querySelector('.modal-overlay');
        const baris = [...overlay.querySelectorAll('.jurnal-baris')]
          .map(row => ({
            akun_id: row.querySelector('.jb-akun').value,
            debit: row.querySelector('.jb-debit').value || '0',
            kredit: row.querySelector('.jb-kredit').value || '0',
          }))
          .filter(b => b.akun_id)
          .map(b => ({ akun_id: Number(b.akun_id), debit: b.debit, kredit: b.kredit }));

        if (baris.length < 2) throw new Error('Minimal 2 baris akun harus diisi.');

        const totalDebit = baris.reduce((s, b) => s + Number(b.debit), 0);
        const totalKredit = baris.reduce((s, b) => s + Number(b.kredit), 0);
        if (totalDebit !== totalKredit) {
          throw new Error(`Debit (${totalDebit}) dan Kredit (${totalKredit}) belum balance.`);
        }

        await this.api.post(`/jurnal-umum/jurnal?petugas_id=1`, { // TODO: ganti ke user login saat modul Pengaturan jadi
          departemen_id: Number(overlay.querySelector('#ju-departemen').value),
          tahun_buku_id: aktif.id,
          tanggal: overlay.querySelector('#ju-tanggal').value,
          keterangan: overlay.querySelector('#ju-keterangan').value,
          baris,
        });
        close();
        this._muatData();
      },
    });

    const overlay = document.querySelector('.modal-overlay');
    const container = overlay.querySelector('#ju-baris-container');

    const perbaruiBalanceInfo = () => {
      const rows = [...overlay.querySelectorAll('.jurnal-baris')];
      const totalDebit = rows.reduce((s, r) => s + Number(r.querySelector('.jb-debit').value || 0), 0);
      const totalKredit = rows.reduce((s, r) => s + Number(r.querySelector('.jb-kredit').value || 0), 0);
      const info = overlay.querySelector('#ju-balance-info');
      const selisih = totalDebit - totalKredit;
      info.textContent = `Debit: ${TableRenderer.formatUang(totalDebit)} | Kredit: ${TableRenderer.formatUang(totalKredit)} | ${selisih === 0 ? 'Balance ✓' : `Selisih: ${TableRenderer.formatUang(Math.abs(selisih))}`}`;
      info.style.color = selisih === 0 ? 'var(--color-success)' : 'var(--color-danger)';
    };

    const wireRow = (row) => {
      row.querySelector('.jb-hapus').addEventListener('click', () => {
        if (overlay.querySelectorAll('.jurnal-baris').length <= 2) {
          window.alert('Minimal 2 baris jurnal.');
          return;
        }
        row.remove();
        perbaruiBalanceInfo();
      });
      row.querySelector('.jb-debit').addEventListener('input', perbaruiBalanceInfo);
      row.querySelector('.jb-kredit').addEventListener('input', perbaruiBalanceInfo);
    };

    container.querySelectorAll('.jurnal-baris').forEach(wireRow);

    overlay.querySelector('#ju-tambah-baris').addEventListener('click', () => {
      container.insertAdjacentHTML('beforeend', this._barisHtml(akunOptionsHtml));
      const baris = [...container.querySelectorAll('.jurnal-baris')];
      wireRow(baris[baris.length - 1]);
      perbaruiBalanceInfo();
    });

    perbaruiBalanceInfo();
  }

  async _batalkanJurnal(jurnalHeaderId) {
    const alasan = window.prompt('Alasan pembatalan jurnal ini:');
    if (!alasan) return;
    try {
      await this.api.post(`/jurnal-umum/jurnal/${jurnalHeaderId}/batalkan?user_id=1`, { alasan }); // TODO: ganti ke user login saat modul Pengaturan jadi
      this._muatData();
    } catch (err) {
      window.alert(`Gagal membatalkan: ${err.message}`);
    }
  }

  destroy() {
    // Tidak ada listener global (interval/websocket) di modul ini, jadi kosong.
  }
}
