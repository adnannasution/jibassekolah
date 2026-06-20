"""
Mesin Jurnal (Ledger Engine).

Semua modul (Penerimaan, Pengeluaran, Jurnal Umum) WAJIB posting lewat
fungsi `posting_jurnal()` di sini. Tidak ada jalur lain untuk insert ke
jurnal_header/jurnal_detail. Ini titik tunggal yang menjamin:
  1. Total debit == total kredit (kalau tidak, transaksi ditolak & di-rollback)
  2. Tahun buku yang statusnya TUTUP tidak bisa lagi ditambah transaksi
  3. Nomor jurnal otomatis & konsisten per departemen + tahun buku
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.models.ledger import JurnalHeader, JurnalDetail, SumberModul, StatusJurnal
from app.models.referensi import TahunBuku, StatusTahunBuku


class JurnalTidakBalanceError(Exception):
    """Total debit dan kredit tidak sama."""


class TahunBukuTutupError(Exception):
    """Tahun buku sudah ditutup, tidak bisa menambah transaksi."""


@dataclass
class BarisJurnal:
    akun_id: int
    debit: Decimal = Decimal("0")
    kredit: Decimal = Decimal("0")


def _generate_no_jurnal(db: Session, departemen_id: int, tahun_buku: TahunBuku, tanggal: date) -> str:
    """Format: {AWALAN_KUITANSI}{urutan 6 digit}, urut per tahun buku."""
    jumlah = (
        db.query(JurnalHeader)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku.id)
        .count()
    )
    urutan = str(jumlah + 1).zfill(6)
    return f"{tahun_buku.awalan_kuitansi}{urutan}"


def posting_jurnal(
    db: Session,
    departemen_id: int,
    tahun_buku_id: int,
    tanggal: date,
    keterangan: str,
    sumber_modul: SumberModul,
    petugas_id: int,
    baris: List[BarisJurnal],
    sumber_id: int | None = None,
) -> JurnalHeader:
    """
    Posting satu transaksi ke jurnal. `baris` minimal 2 baris, total debit
    harus sama dengan total kredit. Mengembalikan JurnalHeader yang sudah
    tersimpan (caller bertanggung jawab commit di luar fungsi ini kalau mau
    digabung dalam satu transaksi DB yang lebih besar).
    """
    tahun_buku = db.query(TahunBuku).filter(TahunBuku.id == tahun_buku_id).first()
    if tahun_buku is None:
        raise ValueError("Tahun buku tidak ditemukan")
    if tahun_buku.status == StatusTahunBuku.TUTUP:
        raise TahunBukuTutupError(
            f"Tahun buku {tahun_buku.tahun_buku} sudah ditutup, transaksi ditolak."
        )

    total_debit = sum((b.debit for b in baris), Decimal("0"))
    total_kredit = sum((b.kredit for b in baris), Decimal("0"))
    if total_debit != total_kredit:
        raise JurnalTidakBalanceError(
            f"Total debit ({total_debit}) tidak sama dengan total kredit ({total_kredit})"
        )
    if total_debit == 0:
        raise JurnalTidakBalanceError("Total transaksi tidak boleh 0")

    header = JurnalHeader(
        no_jurnal=_generate_no_jurnal(db, departemen_id, tahun_buku, tanggal),
        tanggal=tanggal,
        departemen_id=departemen_id,
        tahun_buku_id=tahun_buku_id,
        keterangan=keterangan,
        sumber_modul=sumber_modul,
        sumber_id=sumber_id,
        petugas_id=petugas_id,
        status=StatusJurnal.AKTIF,
    )
    db.add(header)
    db.flush()  # supaya header.id tersedia untuk detail

    for b in baris:
        db.add(JurnalDetail(
            jurnal_header_id=header.id,
            akun_id=b.akun_id,
            debit=b.debit,
            kredit=b.kredit,
        ))

    return header


def batalkan_jurnal(db: Session, jurnal_header_id: int) -> JurnalHeader:
    """
    Pembatalan jurnal tidak menghapus baris (soft-cancel), supaya jejak audit
    tetap utuh. Status diubah jadi DIBATALKAN, dan baris ini dikecualikan dari
    semua laporan/perhitungan saldo.
    """
    header = db.query(JurnalHeader).filter(JurnalHeader.id == jurnal_header_id).first()
    if header is None:
        raise ValueError("Jurnal tidak ditemukan")

    tahun_buku = db.query(TahunBuku).filter(TahunBuku.id == header.tahun_buku_id).first()
    if tahun_buku and tahun_buku.status == StatusTahunBuku.TUTUP:
        raise TahunBukuTutupError("Tahun buku sudah ditutup, jurnal tidak bisa dibatalkan.")

    header.status = StatusJurnal.DIBATALKAN
    return header
