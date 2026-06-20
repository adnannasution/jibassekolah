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

  static render(columns, data, { emptyMessage = 'Belum ada data.' } = {}) {
    if (!data || data.length === 0) {
      return `<div class="empty-state">${emptyMessage}</div>`;
    }

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

    return `
      <table class="data-table">
        <thead><tr>${thead}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }
}
