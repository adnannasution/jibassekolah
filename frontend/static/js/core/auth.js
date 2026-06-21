/**
 * Auth — sesi login sederhana (belum token/JWT, MVP modul Pengaturan).
 * Simpan user yang sedang login di localStorage, dipakai modul lain
 * (Penerimaan, Pengeluaran, Jurnal Umum, Referensi/Tutup Buku) sebagai
 * pengganti placeholder petugas_id=1/user_id=1.
 */
const Auth = {
  KEY: 'jibas_current_user',

  getUser() {
    const raw = localStorage.getItem(this.KEY);
    return raw ? JSON.parse(raw) : null;
  },

  setUser(user) {
    localStorage.setItem(this.KEY, JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem(this.KEY);
  },

  userId() {
    const user = this.getUser();
    return user ? user.id : null;
  },
};
