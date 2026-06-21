"""
Logic modul Pengeluaran. SEMUA posting di sini lewat
app/core/ledger.py::posting_jurnal() -- tidak ada insert langsung ke jurnal.

Beda dengan Penerimaan, modul ini tidak akrual: tiap jenis_pengeluaran
punya mapping tetap (rek_kredit = akun kas, rek_debet = akun biaya), jadi
satu transaksi langsung Debit Biaya, Kredit Kas (lihat CLAUDE.md).
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.audit import catat_audit
from app.core.ledger import BarisJurnal, batalkan_jurnal, posting_jurnal
from app.models.audit import AksiAudit, AuditLog
from app.models.ledger import SumberModul
from app.models.pengeluaran import JenisPengeluaran, Pengeluaran, StatusPengeluaran


class PengeluaranSudahDibatalkanError(Exception):
    """Pengeluaran ini sudah dibatalkan, tidak bisa dibatalkan lagi."""


@dataclass
class BuatPengeluaranRequest:
    jenis_pengeluaran_id: int
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah: Decimal
    keterangan: Optional[str] = None


def _generate_no_kuitansi(db: Session, tahun_buku_id: int) -> str:
    jumlah = db.query(Pengeluaran).filter(Pengeluaran.tahun_buku_id == tahun_buku_id).count()
    return f"PNG{str(jumlah + 1).zfill(6)}"


def buat_pengeluaran(db: Session, request: BuatPengeluaranRequest, petugas_id: int) -> Pengeluaran:
    jenis = db.query(JenisPengeluaran).filter(JenisPengeluaran.id == request.jenis_pengeluaran_id).first()
    if jenis is None:
        raise ValueError("Jenis pengeluaran tidak ditemukan")
    if request.jumlah <= 0:
        raise ValueError("Jumlah pengeluaran harus lebih dari 0")

    no_kuitansi = _generate_no_kuitansi(db, request.tahun_buku_id)
    header = posting_jurnal(
        db=db,
        departemen_id=request.departemen_id,
        tahun_buku_id=request.tahun_buku_id,
        tanggal=request.tanggal,
        keterangan=request.keterangan or f"Pengeluaran {jenis.nama} - {no_kuitansi}",
        sumber_modul=SumberModul.PENGELUARAN,
        petugas_id=petugas_id,
        baris=[
            BarisJurnal(akun_id=jenis.akun_biaya_id, debit=request.jumlah),
            BarisJurnal(akun_id=jenis.akun_kas_id, kredit=request.jumlah),
        ],
    )

    pengeluaran = Pengeluaran(
        no_kuitansi=no_kuitansi,
        jenis_pengeluaran_id=request.jenis_pengeluaran_id,
        departemen_id=request.departemen_id,
        tahun_buku_id=request.tahun_buku_id,
        tanggal=request.tanggal,
        jumlah=request.jumlah,
        keterangan=request.keterangan,
        petugas_id=petugas_id,
        jurnal_header_id=header.id,
    )
    db.add(pengeluaran)
    db.flush()
    header.sumber_id = pengeluaran.id
    catat_audit(
        db, tabel="pengeluaran", record_id=pengeluaran.id, aksi=AksiAudit.BUAT, user_id=petugas_id,
        data_baru={"no_kuitansi": pengeluaran.no_kuitansi, "jumlah": str(pengeluaran.jumlah)},
    )
    return pengeluaran


def batalkan_pengeluaran(db: Session, pengeluaran_id: int, alasan: str, user_id: int) -> Pengeluaran:
    """
    Soft-cancel (lihat CLAUDE.md aturan #2) -- tidak ada hard-delete untuk
    data transaksi keuangan. Jurnal terkait dibatalkan lewat
    batalkan_jurnal(), lalu perubahan dicatat ke audit_log.
    """
    pengeluaran = db.query(Pengeluaran).filter(Pengeluaran.id == pengeluaran_id).first()
    if pengeluaran is None:
        raise ValueError("Pengeluaran tidak ditemukan")
    if pengeluaran.status == StatusPengeluaran.DIBATALKAN:
        raise PengeluaranSudahDibatalkanError(f"Pengeluaran {pengeluaran.no_kuitansi} sudah dibatalkan")

    data_lama = {
        "status": pengeluaran.status.value,
        "jumlah": str(pengeluaran.jumlah),
        "keterangan": pengeluaran.keterangan,
    }

    batalkan_jurnal(db, pengeluaran.jurnal_header_id)
    pengeluaran.status = StatusPengeluaran.DIBATALKAN

    db.add(AuditLog(
        tabel="pengeluaran",
        record_id=pengeluaran.id,
        aksi=AksiAudit.HAPUS,
        data_lama=data_lama,
        data_baru={"status": StatusPengeluaran.DIBATALKAN.value},
        alasan=alasan,
        user_id=user_id,
    ))

    return pengeluaran
