"""Logic Dashboard ringkasan. Murni baca data lewat fungsi-fungsi laporan yang
sudah ada (laporan.py, laporan_penerimaan.py) -- tidak ada query baru yang
menyentuh jurnal_header/jurnal_detail secara langsung untuk hal yang sudah
disediakan fungsi lain, supaya satu sumber kebenaran tetap terjaga."""
from typing import Optional

from sqlalchemy.orm import Session

from app.core import laporan as laporan_core
from app.core import laporan_penerimaan as laporan_penerimaan_core
from app.models.ledger import JurnalHeader, StatusJurnal


def transaksi_terakhir(db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None, limit: int = 10) -> list[dict]:
    """N transaksi terakhir dari jurnal_header (mencakup Penerimaan, Pengeluaran,
    Jurnal Umum, Tutup Buku -- semua sumber modul karena satu pintu jurnal)."""
    query = (
        db.query(JurnalHeader)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
        .filter(JurnalHeader.status == StatusJurnal.AKTIF)
    )
    if departemen_id is not None:
        query = query.filter(JurnalHeader.departemen_id == departemen_id)
    rows = query.order_by(JurnalHeader.tanggal.desc(), JurnalHeader.id.desc()).limit(limit).all()
    return [
        {
            "jurnal_header_id": h.id, "no_jurnal": h.no_jurnal, "tanggal": h.tanggal,
            "keterangan": h.keterangan, "sumber_modul": h.sumber_modul,
            "total": sum(d.debit for d in h.detail),
        }
        for h in rows
    ]


def ringkasan_dashboard(db: Session, tahun_buku_id: int, departemen_id: Optional[int] = None) -> dict:
    """Ringkasan untuk landing page: saldo kas, total siswa menunggak, daftar
    transaksi terakhir, dan data tunggakan per kelas untuk bar chart."""
    arus_kas = laporan_core.arus_kas(db, tahun_buku_id)
    rekap_menunggak = laporan_penerimaan_core.siswa_menunggak_rekap(db, tahun_buku_id, departemen_id)
    tunggakan_kelas = laporan_penerimaan_core.tunggakan_per_kelas(db, tahun_buku_id, departemen_id)

    return {
        "saldo_kas": arus_kas["total_mutasi_bersih"],
        "jumlah_siswa_menunggak": len(rekap_menunggak),
        "total_tunggakan": sum(r["total_sisa"] for r in rekap_menunggak),
        "transaksi_terakhir": transaksi_terakhir(db, tahun_buku_id, departemen_id),
        "tunggakan_per_kelas": tunggakan_kelas,
    }
