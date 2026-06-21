/**
 * TableRenderer — generate <table> dari definisi kolom + data, dipakai semua modul.
 *
 * columns: [{ key, label, type: 'text'|'uang'|'badge'|'aksi', render? }]
 * type 'uang'  -> diformat Rp + rata kanan monospace otomatis
 * type 'badge' -> render.badgeMap = { value: 'success'|'danger'|'warning'|'neutral' }
 * type 'aksi'  -> render(row) harus mengembalikan HTML tombol-tombol aksi
 */
class TableRenderer {
  static formatUang(angka) {
    const n = Number(angka || 0);
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(n);
  }

  static render(columns, data, { emptyMessage = 'Belum ada data.', searchable = false, searchPlaceholder = 'Cari...' } = {}) {
    if (!data || data.length === 0) {
      return `<div class="empty-state">${emptyMessage}</div>`;
    }

    const tableId = `tbl-${Math.random().toString(36).slice(2, 9)}`;
    const thead = columns.map(c => `<th class="${c.type === 'uang' ? 'num' : ''}">${c.label}</th>`).join('');

    const rows = data.map(row => {
      const cells = columns.map(c => {
        if (c.type === 'uang') {
          return `<td class="uang">${TableRenderer.formatUang(row[c.key])}</td>`;
        }
        if (c.type === 'badge') {
          const variant = (c.badgeMap && c.badgeMap[row[c.key]]) || 'neutral';
          return `<td><span class="badge badge--${variant}">${row[c.key] ?? '-'}</span></td>`;
        }
        if (c.type === 'aksi') {
          return `<td>${c.render(row)}</td>`;
        }
        if (typeof c.render === 'function') {
          return `<td>${c.render(row)}</td>`;
        }
        return `<td>${row[c.key] ?? '-'}</td>`;
      }).join('');
      return `<tr data-id="${row.id ?? ''}">${cells}</tr>`;
    }).join('');

    const searchHtml = searchable ? `
      <div class="table-search">
        <input type="text" class="table-search__input" data-table-search="${tableId}" placeholder="${searchPlaceholder}" />
      </div>
    ` : '';

    return `
      ${searchHtml}
      <table class="data-table" id="${tableId}">
        <thead><tr>${thead}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }

  /** Pasang listener search client-side. Panggil SETELAH innerHTML diisi hasil render(). */
  static attachSearch(container) {
    container.querySelectorAll('[data-table-search]').forEach(input => {
      const table = container.querySelector(`#${input.dataset.tableSearch}`);
      if (!table) return;
      input.addEventListener('input', () => {
        const kata = input.value.trim().toLowerCase();
        table.querySelectorAll('tbody tr').forEach(tr => {
          tr.style.display = tr.textContent.toLowerCase().includes(kata) ? '' : 'none';
        });
      });
    });
  }
}
