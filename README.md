# JIBAS Keuangan (Versi Modern)

Rebuild aplikasi Sistem Informasi Keuangan Sekolah (SIMKEU) dari konsep JIBAS
versi lama, dengan arsitektur ledger terpusat (mesin jurnal) + SPA modular.

## Status

**Fondasi selesai & teruji:**
- Mesin jurnal (`app/core/ledger.py`) — posting transaksi + validasi balance debit=kredit
- Proses Tutup Tahun Buku (`app/core/tutup_buku.py`) — hitung laba/rugi, jurnal penutup, kunci periode lama
- Modul **Referensi** end-to-end: Departemen, Kode Rekening Perkiraan (Akun), Tahun Buku
- Model database lengkap untuk semua modul (termasuk Siswa & Calon Siswa, siap dipakai modul Penerimaan)
- Migration (Alembic) sudah di-generate & diuji

**Belum dibangun** (lanjutan, ikuti pola modul Referensi):
Siswa & Calon Siswa, Penerimaan, Pengeluaran, Jurnal Umum, Laporan Keuangan, Inventory, Pengaturan.

## Menjalankan secara lokal

```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # isi DATABASE_URL sesuai PostgreSQL kamu (atau pakai Railway)

# Buat skema database
python -m alembic upgrade head

# Jalankan server (otomatis serve frontend juga, lewat StaticFiles)
uvicorn app.main:app --reload --app-dir .
```

Buka `http://localhost:8000` — frontend SPA + API jalan dari satu server yang sama.
Dokumentasi API otomatis ada di `http://localhost:8000/docs`.

## Struktur Proyek

```
backend/
  app/
    database.py     -> koneksi PostgreSQL
    core/
      ledger.py      -> mesin jurnal (SEMUA modul transaksi posting lewat sini)
      tutup_buku.py   -> proses tutup tahun buku
    models/           -> SQLAlchemy models per domain
    schemas/          -> Pydantic (request/response)
    routers/          -> 1 router per modul, panggil app/core untuk posting
  alembic/            -> migration

frontend/
  index.html          -> shell SPA (satu halaman, tidak reload)
  static/js/
    core/
      api-client.js    -> wrapper fetch terpusat
      router.js         -> routing hash-based, tanpa reload
    components/         -> TableRenderer, FormBuilder, Modal (reusable semua modul)
    modules/             -> 1 file per modul, extend pola yang sama (lihat referensi.js)
```

## Deploy ke Railway

1. Buat project baru di Railway, tambahkan plugin **PostgreSQL** (Railway otomatis
   menyediakan env var `DATABASE_URL`).
2. Hubungkan repo ini sebagai service. Railway akan memakai `railway.json` /
   `Procfile` di root repo, yang sudah diatur untuk:
   - install dependency dari `backend/requirements.txt`
   - jalankan `alembic upgrade head` (migrasi schema) sebelum start
   - jalankan `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Tidak perlu env var tambahan selain `DATABASE_URL` (sudah otomatis dari plugin Postgres).
4. Setelah deploy sukses, buka domain Railway-nya — frontend SPA + API jalan dari satu service.

## Menambah modul baru

Ikuti pola `ReferensiModule` di `frontend/static/js/modules/`:
1. Buat class baru dengan `constructor(container, api, params)`, method `render()`, dan `destroy()`
2. Daftarkan di `frontend/static/js/app.js` lewat `router.register(...)`
3. Tambahkan `<script>` tag-nya di `index.html`
4. Di backend: buat model di `app/models/`, schema di `app/schemas/`, router di `app/routers/`,
   lalu `app.include_router(...)` di `app/main.py`. Generate migration baru dengan:
   `python -m alembic revision --autogenerate -m "nama perubahan"`

## Prinsip Desain

- **Satu mesin jurnal**: semua modul transaksi (Penerimaan, Pengeluaran, Jurnal Umum) WAJIB
  posting lewat `app/core/ledger.py::posting_jurnal()`. Tidak ada jalur insert lain ke jurnal.
- **Tidak ada hard-delete** untuk data transaksi keuangan — gunakan `batalkan_jurnal()` (soft-cancel)
  supaya jejak audit tetap utuh.
- **Tahun Buku terkunci** setelah ditutup — `posting_jurnal()` otomatis menolak transaksi baru
  ke tahun buku berstatus TUTUP.
- **Laporan = query, bukan tabel hasil hitung** — Buku Besar, Neraca, Rugi Laba dll selalu
  dihitung langsung dari `jurnal_detail`, supaya selalu akurat tanpa proses sinkronisasi terpisah.
