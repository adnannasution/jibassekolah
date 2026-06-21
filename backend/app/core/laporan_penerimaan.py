"""
Logic Laporan Penerimaan. Berbeda dari app/core/laporan.py (yang query
jurnal_detail) -- laporan di sini query langsung dari tabel Tagihan dan
PembayaranTagihan, karena yang dibutuhkan adalah sudut pandang siswa/kelas,
bukan akun jurnal. Tetap live query, tidak ada tabel hasil hitung terpisah.

Definisi "siswa menunggak" untuk MVP: Tagihan.status == BELUM_LUNAS dan
sisa > 0. Model Tagihan belum punya field jatuh tempo, jadi belum bisa
membedakan "menunggak" vs "belum jatuh tempo" -- cukup untuk MVP.
"""
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.penerimaan import PembayaranTagihan, StatusPembayaran, StatusTagihan, Tagihan
from app.models.siswa import Kelas, Siswa


def tagihan_per_kelas(db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None) -> list[dict]:
    """Rekap tagihan per kelas: total ditagihkan, diskon, sisa, jumlah tagihan."""
    query = (
        db.query(
            Kelas.id, Kelas.nama, Kelas.tingkat,
            func.coalesce(func.sum(Tagihan.jumlah_tagihan), 0),
            func.coalesce(func.sum(Tagihan.diskon), 0),
            func.coalesce(func.sum(Tagihan.sisa), 0),
            func.count(Tagihan.id),
        )
        .join(Siswa, Siswa.id == Tagihan.siswa_id)
        .join(Kelas, Kelas.id == Siswa.kelas_id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.status != StatusTagihan.DIBATALKAN)
    )
    if departemen_id is not None:
        query = query.filter(Tagihan.departemen_id == departemen_id)
    rows = query.group_by(Kelas.id, Kelas.nama, Kelas.tingkat).order_by(Kelas.tingkat, Kelas.nama).all()
    return [
        {
            "kelas_id": kelas_id, "kelas_nama": nama, "tingkat": tingkat,
            "total_tagihan": total_tagihan, "total_diskon": total_diskon,
            "total_sisa": total_sisa, "jumlah_tagihan": jumlah_tagihan,
        }
        for kelas_id, nama, tingkat, total_tagihan, total_diskon, total_sisa, jumlah_tagihan in rows
    ]


def tagihan_per_siswa_detail(db: Session, tahun_buku_id: int, siswa_id: int) -> list[dict]:
    """Detail semua tagihan satu siswa di tahun buku tertentu."""
    rows = (
        db.query(Tagihan)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.siswa_id == siswa_id)
        .order_by(Tagihan.tanggal)
        .all()
    )
    return [
        {
            "tagihan_id": t.id, "no_tagihan": t.no_tagihan, "tanggal": t.tanggal,
            "jenis_pembayaran_nama": t.jenis_pembayaran.nama,
            "jumlah_tagihan": t.jumlah_tagihan, "diskon": t.diskon,
            "sisa": t.sisa, "status": t.status,
        }
        for t in rows
    ]


def tagihan_rekap_per_siswa(db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None) -> list[dict]:
    """Rekap total tagihan per siswa (tanpa drill-down ke tagihan_id)."""
    query = (
        db.query(
            Siswa.id, Siswa.nis, Siswa.nama, Kelas.nama,
            func.coalesce(func.sum(Tagihan.jumlah_tagihan), 0),
            func.coalesce(func.sum(Tagihan.diskon), 0),
            func.coalesce(func.sum(Tagihan.sisa), 0),
        )
        .join(Tagihan, Tagihan.siswa_id == Siswa.id)
        .join(Kelas, Kelas.id == Siswa.kelas_id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.status != StatusTagihan.DIBATALKAN)
    )
    if departemen_id is not None:
        query = query.filter(Tagihan.departemen_id == departemen_id)
    rows = query.group_by(Siswa.id, Siswa.nis, Siswa.nama, Kelas.nama).order_by(Siswa.nama).all()
    return [
        {
            "siswa_id": siswa_id, "nis": nis, "nama": nama, "kelas_nama": kelas_nama,
            "total_tagihan": total_tagihan, "total_diskon": total_diskon, "total_sisa": total_sisa,
        }
        for siswa_id, nis, nama, kelas_nama, total_tagihan, total_diskon, total_sisa in rows
    ]


def _query_siswa_menunggak(db: Session, tahun_buku_id: int, departemen_id: Optional[int], kelas_id: Optional[int]):
    query = (
        db.query(Tagihan)
        .join(Siswa, Siswa.id == Tagihan.siswa_id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.status == StatusTagihan.BELUM_LUNAS)
        .filter(Tagihan.sisa > 0)
    )
    if departemen_id is not None:
        query = query.filter(Tagihan.departemen_id == departemen_id)
    if kelas_id is not None:
        query = query.filter(Siswa.kelas_id == kelas_id)
    return query


def siswa_menunggak_detail(
    db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None, kelas_id: Optional[int] = None
) -> list[dict]:
    """Daftar tagihan yang masih menunggak (BELUM_LUNAS, sisa > 0), satu baris per tagihan."""
    rows = _query_siswa_menunggak(db, tahun_buku_id, departemen_id, kelas_id).order_by(Tagihan.tanggal).all()
    return [
        {
            "tagihan_id": t.id, "no_tagihan": t.no_tagihan, "tanggal": t.tanggal,
            "siswa_id": t.siswa_id, "siswa_nama": t.siswa.nama, "siswa_nis": t.siswa.nis,
            "kelas_nama": t.siswa.kelas.nama,
            "jenis_pembayaran_nama": t.jenis_pembayaran.nama,
            "sisa": t.sisa,
        }
        for t in rows
    ]


def siswa_menunggak_rekap(
    db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None
) -> list[dict]:
    """Rekap total tunggakan per siswa (dipakai dashboard & rekap laporan)."""
    query = (
        db.query(
            Siswa.id, Siswa.nis, Siswa.nama, Kelas.nama,
            func.coalesce(func.sum(Tagihan.sisa), 0),
            func.count(Tagihan.id),
        )
        .join(Tagihan, Tagihan.siswa_id == Siswa.id)
        .join(Kelas, Kelas.id == Siswa.kelas_id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.status == StatusTagihan.BELUM_LUNAS)
        .filter(Tagihan.sisa > 0)
    )
    if departemen_id is not None:
        query = query.filter(Tagihan.departemen_id == departemen_id)
    rows = query.group_by(Siswa.id, Siswa.nis, Siswa.nama, Kelas.nama).order_by(Siswa.nama).all()
    return [
        {
            "siswa_id": siswa_id, "nis": nis, "nama": nama, "kelas_nama": kelas_nama,
            "total_sisa": total_sisa, "jumlah_tagihan_menunggak": jumlah_tagihan,
        }
        for siswa_id, nis, nama, kelas_nama, total_sisa, jumlah_tagihan in rows
    ]


def tunggakan_per_kelas(db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None) -> list[dict]:
    """Rekap total tunggakan per kelas -- dipakai bar chart Dashboard."""
    query = (
        db.query(
            Kelas.id, Kelas.nama,
            func.coalesce(func.sum(Tagihan.sisa), 0),
        )
        .join(Siswa, Siswa.id == Tagihan.siswa_id)
        .join(Kelas, Kelas.id == Siswa.kelas_id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.status == StatusTagihan.BELUM_LUNAS)
        .filter(Tagihan.sisa > 0)
    )
    if departemen_id is not None:
        query = query.filter(Tagihan.departemen_id == departemen_id)
    rows = query.group_by(Kelas.id, Kelas.nama).order_by(Kelas.nama).all()
    return [
        {"kelas_id": kelas_id, "kelas_nama": nama, "total_sisa": total_sisa}
        for kelas_id, nama, total_sisa in rows
    ]


def rekapitulasi_penerimaan(
    db: Session,
    tahun_buku_id: int,
    departemen_id: Optional[int] = None,
    tanggal_mulai=None,
    tanggal_selesai=None,
) -> list[dict]:
    """Rekap per jenis pembayaran: total ditagihkan (Tagihan) vs total
    diterima tunai (PembayaranTagihan status AKTIF), opsional difilter rentang
    tanggal pembayaran."""
    from app.models.penerimaan import JenisPembayaran

    tagihan_query = (
        db.query(
            JenisPembayaran.id, JenisPembayaran.nama,
            func.coalesce(func.sum(Tagihan.jumlah_tagihan - Tagihan.diskon), 0),
        )
        .join(Tagihan, Tagihan.jenis_pembayaran_id == JenisPembayaran.id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(Tagihan.status != StatusTagihan.DIBATALKAN)
    )
    if departemen_id is not None:
        tagihan_query = tagihan_query.filter(Tagihan.departemen_id == departemen_id)
    tagihan_rows = tagihan_query.group_by(JenisPembayaran.id, JenisPembayaran.nama).all()
    ditagihkan_map = {jp_id: (nama, total) for jp_id, nama, total in tagihan_rows}

    diterima_query = (
        db.query(
            JenisPembayaran.id,
            func.coalesce(func.sum(PembayaranTagihan.jumlah_bayar), 0),
        )
        .join(Tagihan, Tagihan.jenis_pembayaran_id == JenisPembayaran.id)
        .join(PembayaranTagihan, PembayaranTagihan.tagihan_id == Tagihan.id)
        .filter(Tagihan.tahun_buku_id == tahun_buku_id)
        .filter(PembayaranTagihan.status == StatusPembayaran.AKTIF)
    )
    if departemen_id is not None:
        diterima_query = diterima_query.filter(Tagihan.departemen_id == departemen_id)
    if tanggal_mulai is not None:
        diterima_query = diterima_query.filter(PembayaranTagihan.tanggal >= tanggal_mulai)
    if tanggal_selesai is not None:
        diterima_query = diterima_query.filter(PembayaranTagihan.tanggal <= tanggal_selesai)
    diterima_rows = diterima_query.group_by(JenisPembayaran.id).all()
    diterima_map = {jp_id: total for jp_id, total in diterima_rows}

    semua_id = set(ditagihkan_map) | set(diterima_map)
    hasil = []
    for jp_id in semua_id:
        nama, total_ditagihkan = ditagihkan_map.get(jp_id, (None, Decimal("0")))
        if nama is None:
            from app.models.penerimaan import JenisPembayaran as JP
            nama = db.query(JP.nama).filter(JP.id == jp_id).scalar()
        total_diterima = diterima_map.get(jp_id, Decimal("0"))
        hasil.append({
            "jenis_pembayaran_id": jp_id, "jenis_pembayaran_nama": nama,
            "total_ditagihkan": total_ditagihkan, "total_diterima": total_diterima,
        })
    hasil.sort(key=lambda r: r["jenis_pembayaran_nama"] or "")
    return hasil
