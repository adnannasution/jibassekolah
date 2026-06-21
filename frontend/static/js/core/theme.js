/**
 * Theme — preferensi preset warna tampilan, disimpan di localStorage
 * (per-browser, sama seperti Auth, tidak ada sinkronisasi server). Preset
 * cuma mengubah warna primer/sidebar lewat atribut [data-theme] di <html>
 * (lihat tokens.css) — bukan color picker bebas, supaya kombinasi warna
 * selalu konsisten/kontras aman.
 */
const Theme = {
  KEY: 'jibas_theme',
  DAFTAR: [
    { key: 'default', label: 'Navy & Emas' },
    { key: 'hijau', label: 'Hijau Tua & Emas' },
    { key: 'maroon', label: 'Maroon & Emas' },
    { key: 'biru-laut', label: 'Biru Laut & Emas' },
  ],

  get() {
    return localStorage.getItem(this.KEY) || 'default';
  },

  set(key) {
    localStorage.setItem(this.KEY, key);
    this.terapkan();
  },

  terapkan() {
    document.documentElement.setAttribute('data-theme', this.get());
  },
};
