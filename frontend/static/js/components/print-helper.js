/**
 * PrintHelper — komponen cetak bersama (Kuitansi Pengeluaran & Export Laporan
 * ke PDF). Strategi browser-native: isi #print-area lalu panggil window.print(),
 * styling cetak diatur di print.css. Tidak menambah dependency PDF baru.
 */
class PrintHelper {
  static cetak(titleHtml, bodyHtml) {
    let area = document.getElementById('print-area');
    if (!area) {
      area = document.createElement('div');
      area.id = 'print-area';
      document.body.appendChild(area);
    }
    area.innerHTML = `${titleHtml}${bodyHtml}`;
    window.print();
  }
}
