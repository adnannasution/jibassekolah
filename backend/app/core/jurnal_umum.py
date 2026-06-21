"""
Logic modul Jurnal Umum. Posting tetap lewat app/core/ledger.py::posting_jurnal()
-- modul ini cuma wrapper tipis supaya baris-baris akun (debit/kredit, bebas
berapa pun jumlahnya & akun apa pun) yang diinput manual lewat UI tetap lewat
satu pintu jurnal yang sama dengan Penerimaan/Pengeluaran.
"""
from dataclasses import dataclass
from datetime import date
from typing import List

from sqlalchemy.orm import Session

from app.core.audit import catat_audit
from app.core.ledger import BarisJurnal, batalkan_jurnal, posting_jurnal
from app.models.audit import AksiAudit, AuditLog
from app.models.ledger import JurnalHeader, StatusJurnal, SumberModul


class JurnalSudahDibatalkanError(Exception):
    """Jurnal ini sudah dibatalkan, tidak bisa dibatalkan lagi."""


@dataclass
class BuatJurnalUmumRequest:
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    keterangan: str
    baris: List[BarisJurnal]


def buat_jurnal_umum(db: Session, request: BuatJurnalUmumRequest, petugas_id: int) -> JurnalHeader:
    header = posting_jurnal(
        db=db,
        departemen_id=request.departemen_id,
        tahun_buku_id=request.tahun_buku_id,
        tanggal=request.tanggal,
        keterangan=request.keterangan,
        sumber_modul=SumberModul.JURNAL_UMUM,
        petugas_id=petugas_id,
        baris=request.baris,
    )
    catat_audit(
        db, tabel="jurnal_header", record_id=header.id, aksi=AksiAudit.BUAT, user_id=petugas_id,
        data_baru={"no_jurnal": header.no_jurnal, "keterangan": header.keterangan},
    )
    return header


def batalkan_jurnal_umum(db: Session, jurnal_header_id: int, alasan: str, user_id: int) -> JurnalHeader:
    """
    Soft-cancel (lihat CLAUDE.md aturan #2) -- tidak ada hard-delete untuk
    data transaksi keuangan. batalkan_jurnal() sudah menangani validasi
    tahun buku tutup, di sini cuma ditambah pengecekan double-cancel +
    pencatatan audit_log.
    """
    header = db.query(JurnalHeader).filter(JurnalHeader.id == jurnal_header_id).first()
    if header is None:
        raise ValueError("Jurnal tidak ditemukan")
    if header.status == StatusJurnal.DIBATALKAN:
        raise JurnalSudahDibatalkanError(f"Jurnal {header.no_jurnal} sudah dibatalkan")

    data_lama = {
        "status": header.status.value,
        "keterangan": header.keterangan,
    }

    batalkan_jurnal(db, jurnal_header_id)

    db.add(AuditLog(
        tabel="jurnal_header",
        record_id=header.id,
        aksi=AksiAudit.HAPUS,
        data_lama=data_lama,
        data_baru={"status": StatusJurnal.DIBATALKAN.value},
        alasan=alasan,
        user_id=user_id,
    ))

    return header
