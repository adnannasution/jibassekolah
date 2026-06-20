# JIBAS Keuangan — Konteks Proyek

@README.md

Baca README di atas dulu untuk struktur folder, cara jalanin lokal, dan status
terkini. Bagian di bawah ini isinya hal-hal yang TIDAK ada di README — keputusan
konsep dan aturan domain yang harus selalu diikuti tiap nambah modul baru.

## Apa proyek ini

Rebuild modern dari JIBAS Keuangan (SIMKEU) — sistem informasi keuangan sekolah
double-entry, multi-departemen (SMA/SMP/TK dst). Konsep akuntansinya mengikuti
manual JIBAS versi lama persis (lihat logic di bawah), cuma arsitekturnya
dimodernisasi: satu mesin jurnal terpusat + SPA modular, bukan logic jurnal
terpisah per modul seperti versi lama.

## Aturan yang TIDAK BOLEH dilanggar

1. **Satu pintu jurnal.** Semua transaksi keuangan (Penerimaan, Pengeluaran,
   Jurnal Umum) WAJIB posting lewat `posting_jurnal()` di
   `backend/app/core/ledger.py`. Jangan pernah insert langsung ke
   `jurnal_header`/`jurnal_detail` dari router atau tempat lain.
2. **Tidak ada hard-delete** untuk data transaksi keuangan. Pakai
   `batalkan_jurnal()` (soft-cancel, status DIBATALKAN) + catat perubahan ke
   `audit_log` (tabel, record_id, data_lama, data_baru, alasan, user_id).
3. **Tahun buku terkunci.** `posting_jurnal()` otomatis menolak transaksi baru
   ke tahun buku berstatus TUTUP — jangan bypass validasi ini.
4. **Frontend vanilla JS, BUKAN React/Next.js/framework apa pun.** SPA
   hash-router tanpa reload halaman. Pakai `frontend/static/js/modules/referensi.js`
   sebagai TEMPLATE pola modul baru (constructor(container, api, params),
   render(), destroy()). Komponen reusable: `TableRenderer`, `FormBuilder`, `Modal`
   — jangan bikin ulang pola tabel/form dari nol di modul baru.
5. **Bahasa Indonesia** untuk semua komentar kode, pesan error, dan teks UI.
6. Sebelum bilang sebuah modul "selesai": jalankan smoke test nyata (bikin
   skema via `Base.metadata.create_all`, posting transaksi contoh, cek validasi
   balance/lock-nya jalan) — bukan cuma nulis kode tanpa dites. Ikuti pola test
   yang sudah dipakai pas bangun modul Referensi.
7. Tiap model baru: generate migration dengan
   `alembic revision --autogenerate -m "..."`. Jangan ubah skema database manual.
8. Edit file yang sudah ada secara targeted (pakai diff/patch ke bagian yang
   relevan). Jangan rewrite seluruh file kalau cuma nambah/ubah satu fungsi.

## Logic akuntansi domain (PENTING — sumber bug paling sering kalau salah)

Pengakuan transaksi di modul Penerimaan HARUS akrual, bukan kas basis:

- **Tagihan dibuat** (jumlah pembayaran diinput pertama kali, status belum lunas)
  → Debit `Piutang`, Kredit `Pendapatan` (pendapatan diakui penuh di muka,
  walau belum dibayar tunai)
- **Cicilan masuk** → Debit `Kas`, Kredit `Piutang` (TIDAK menyentuh akun
  Pendapatan lagi, karena sudah diakui di langkah pertama)
- **Lunas langsung** (gak lewat proses piutang/cicilan) → Debit `Kas`,
  Kredit `Pendapatan` langsung
- **Pembayaran tunggakan setelah tutup buku** → tetap Debit `Kas`,
  Kredit `Piutang Siswa`
- **Diskon**: mengurangi nominal cicilan yang harus dibayar siswa — belum
  diputuskan apakah perlu akun "Potongan" terpisah atau cukup pengurang
  Piutang langsung. Putuskan konsisten sebelum implementasi Penerimaan.

Modul Pengeluaran: tiap `jenis_pengeluaran` punya mapping tetap
(`rek_kredit` = akun kas, `rek_debet` = akun biaya) — posting langsung sesuai
mapping itu, gak ada logic akrual seperti Penerimaan.

Tutup Buku: hitung laba/rugi (Pendapatan − Biaya) dari `jurnal_detail` yang
ter-scope ke `tahun_buku_id` yang ditutup, posting net-nya ke akun Retained
Earning lawan akun Modal, kunci tahun buku lama, buat tahun buku baru AKTIF.
Implementasi saat ini menyederhanakan (tidak nolin akun Pendapatan/Biaya
satu-satu lewat akun perantara) — cukup untuk MVP karena laporan tetap akurat
(di-scope per tahun_buku_id).

## Roadmap modul (urutan pengerjaan, modul belakang bergantung modul depan)

1. ✅ Referensi — Departemen, Kode Rekening Perkiraan, Tahun Buku, Tutup Buku
2. ⬜ Siswa & Calon Siswa — model sudah ada (`models/siswa.py`: Kelas, Siswa,
   KelompokCalonSiswa, CalonSiswa), router & frontend belum dibuat. Dipakai
   modul Penerimaan untuk pilih siapa yang bayar.
3. ⬜ Penerimaan — pakai pola akrual di atas, dukung cicilan, diskon,
   pembayaran sisa tunggakan, plus ~10 jenis laporan (per kelas, per siswa,
   siswa menunggak, rekapitulasi, dst — lihat manual asli)
4. ⬜ Pengeluaran — jenis pengeluaran, pembayaran + cetak kuitansi
5. ⬜ Jurnal Umum — UI baris dinamis (tambah/hapus baris akun), validasi
   balance real-time di frontend sebelum submit
6. ⬜ Laporan Keuangan — Buku Besar, Rugi Laba, Neraca Percobaan, Perubahan
   Modal, Neraca, Arus Kas, Audit Perubahan Data. SEMUA laporan dihitung
   query langsung dari `jurnal_detail`, JANGAN bikin tabel hasil hitung terpisah.
7. ⬜ Inventory — group barang hierarkis + data barang (gak nyentuh jurnal)
8. ⬜ Pengaturan — user & role (admin/manajer/staf), scoped per departemen

## Desain visual

Token warna/tipografi ada di `frontend/static/css/tokens.css` — konsep
"kertas dingin" (bukan cream hangat generik), navy primary + aksen
brass/kuningan, serif Georgia buat heading, badge bergaya "stempel buku besar"
(dashed border). Ikuti token yang sudah ada, jangan introduce palet baru per modul.
