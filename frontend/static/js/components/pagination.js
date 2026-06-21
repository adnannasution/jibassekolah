/**
 * Pagination — komponen reusable untuk search (server-side) + kontrol halaman,
 * dipakai modul yang endpoint-nya sudah mendukung query param cari/halaman/ukuran_halaman
 * dan membalas bentuk HalamanOut (items, total, halaman, ukuran_halaman).
 */
class Pagination {
  /** Render search box + info halaman + tombol sebelum/selanjutnya. */
  static renderControls({ cari = '', halaman = 1, total = 0, ukuranHalaman = 20, searchPlaceholder = 'Cari...' } = {}) {
    const totalHalaman = Math.max(1, Math.ceil(total / ukuranHalaman));
    return `
      <div class="table-search flex-between" style="gap: var(--space-3); flex-wrap: wrap;">
        <input type="text" class="table-search__input" data-pg-cari value="${cari.replace(/"/g, '&quot;')}" placeholder="${searchPlaceholder}" />
        <div style="display:flex; align-items:center; gap: var(--space-2);">
          <button class="btn btn-outline btn-sm" data-pg-prev ${halaman <= 1 ? 'disabled' : ''}>&laquo; Sebelumnya</button>
          <span class="text-muted">Halaman ${halaman} dari ${totalHalaman} (${total} baris)</span>
          <button class="btn btn-outline btn-sm" data-pg-next ${halaman >= totalHalaman ? 'disabled' : ''}>Selanjutnya &raquo;</button>
        </div>
      </div>
    `;
  }

  /**
   * Pasang listener pada kontrol yang sudah di-render di dalam `container`.
   * `state` adalah object { cari, halaman } milik modul pemanggil (dimutasi langsung).
   * `onChange` dipanggil tiap kali state berubah (modul lalu memuat ulang data).
   */
  static attach(container, state, onChange) {
    const input = container.querySelector('[data-pg-cari]');
    if (input) {
      let timer = null;
      input.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          state.cari = input.value.trim();
          state.halaman = 1;
          onChange();
        }, 350);
      });
    }
    const prev = container.querySelector('[data-pg-prev]');
    if (prev) {
      prev.addEventListener('click', () => {
        if (state.halaman <= 1) return;
        state.halaman -= 1;
        onChange();
      });
    }
    const next = container.querySelector('[data-pg-next]');
    if (next) {
      next.addEventListener('click', () => {
        state.halaman += 1;
        onChange();
      });
    }
  }
}
