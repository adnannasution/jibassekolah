"""
Logic akrual modul Penerimaan. SEMUA posting di sini lewat
app/core/ledger.py::posting_jurnal() -- tidak ada insert langsung ke jurnal.

Tiga skenario (lihat CLAUDE.md):
1. Tagihan dibuat (langsung_lunas=False) -> Debit Piutang, Kredit Pendapatan
   sebesar (jumlah_tagihan - diskon). Status BELUM_LUNAS, sisa = net.
2. Cicilan/pelunasan tagihan -> Debit Kas, Kredit Piutang. Tidak menyentuh
   Pendapatan lagi (sudah diakui di langkah 1). Berlaku juga untuk pembayaran
   tunggakan setelah tutup buku -- bedanya cuma tahun_buku_id pembayaran
   memakai tahun buku AKTIF saat ini, bukan tahun buku tagihan asal.
3. Lunas langsung (langsung_lunas=True) -> tanpa Piutang sama sekali,
   langsung Debit Kas, Kredit Pendapatan. Status langsung LUNAS, sisa = 0.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.audit import catat_audit
from app.core.ledger import BarisJurnal, posting_jurnal
from app.models.audit import AksiAudit
from app.models.ledger import SumberModul
from app.models.penerimaan import (
    JenisPembayaran, PembayaranTagihan, StatusPembayaran, StatusTagihan, Tagihan,
)


class TagihanSudahLunasError(Exception):
    """Tagihan ini sudah lunas/dibatalkan, tidak bisa dibayar lagi."""


class JumlahBayarTidakValidError(Exception):
    """Jumlah bayar lebih besar dari sisa tagihan, atau <= 0."""


@dataclass
class BuatTagihanRequest:
    siswa_id: int
    jenis_pembayaran_id: int
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah_tagihan: Decimal
    diskon: Decimal = Decimal("0")
    langsung_lunas: bool = False
    akun_kas_id: Optional[int] = None  # wajib kalau langsung_lunas=True
    keterangan: Optional[str] = None


def _generate_no_tagihan(db: Session, tahun_buku_id: int) -> str:
    jumlah = db.query(Tagihan).filter(Tagihan.tahun_buku_id == tahun_buku_id).count()
    return f"TGH{str(jumlah + 1).zfill(6)}"


def buat_tagihan(db: Session, request: BuatTagihanRequest, petugas_id: int) -> Tagihan:
    jenis = db.query(JenisPembayaran).filter(JenisPembayaran.id == request.jenis_pembayaran_id).first()
    if jenis is None:
        raise ValueError("Jenis pembayaran tidak ditemukan")

    net = request.jumlah_tagihan - request.diskon
    if net <= 0:
        raise JumlahBayarTidakValidError("Jumlah tagihan setelah diskon harus lebih dari 0")

    if request.langsung_lunas:
        if request.akun_kas_id is None:
            raise ValueError("akun_kas_id wajib diisi untuk pembayaran lunas langsung")
        baris = [
            BarisJurnal(akun_id=request.akun_kas_id, debit=net),
            BarisJurnal(akun_id=jenis.akun_pendapatan_id, kredit=net),
        ]
        status = StatusTagihan.LUNAS
        sisa = Decimal("0")
    else:
        baris = [
            BarisJurnal(akun_id=jenis.akun_piutang_id, debit=net),
            BarisJurnal(akun_id=jenis.akun_pendapatan_id, kredit=net),
        ]
        status = StatusTagihan.BELUM_LUNAS
        sisa = net

    no_tagihan = _generate_no_tagihan(db, request.tahun_buku_id)
    header = posting_jurnal(
        db=db,
        departemen_id=request.departemen_id,
        tahun_buku_id=request.tahun_buku_id,
        tanggal=request.tanggal,
        keterangan=request.keterangan or f"Tagihan {jenis.nama} - {no_tagihan}",
        sumber_modul=SumberModul.PENERIMAAN,
        petugas_id=petugas_id,
        baris=baris,
    )

    tagihan = Tagihan(
        no_tagihan=no_tagihan,
        siswa_id=request.siswa_id,
        jenis_pembayaran_id=request.jenis_pembayaran_id,
        departemen_id=request.departemen_id,
        tahun_buku_id=request.tahun_buku_id,
        tanggal=request.tanggal,
        jumlah_tagihan=request.jumlah_tagihan,
        diskon=request.diskon,
        sisa=sisa,
        status=status,
        keterangan=request.keterangan,
        jurnal_header_id=header.id,
    )
    db.add(tagihan)
    db.flush()
    header.sumber_id = tagihan.id
    catat_audit(
        db, tabel="tagihan", record_id=tagihan.id, aksi=AksiAudit.BUAT, user_id=petugas_id,
        data_baru={"no_tagihan": tagihan.no_tagihan, "jumlah_tagihan": str(tagihan.jumlah_tagihan), "status": tagihan.status.value},
    )
    return tagihan


def bayar_tagihan(
    db: Session,
    tagihan_id: int,
    tahun_buku_id: int,
    tanggal: date,
    jumlah_bayar: Decimal,
    akun_kas_id: int,
    petugas_id: int,
    keterangan: Optional[str] = None,
) -> PembayaranTagihan:
    """
    `tahun_buku_id` adalah tahun buku AKTIF saat pembayaran terjadi -- bisa
    berbeda dari tahun_buku_id milik tagihan kalau ini pembayaran tunggakan
    setelah tutup buku (posting_jurnal tetap menolak kalau tahun_buku_id yang
    dikirim ternyata sudah TUTUP).
    """
    tagihan = db.query(Tagihan).filter(Tagihan.id == tagihan_id).first()
    if tagihan is None:
        raise ValueError("Tagihan tidak ditemukan")
    if tagihan.status != StatusTagihan.BELUM_LUNAS:
        raise TagihanSudahLunasError(f"Tagihan {tagihan.no_tagihan} statusnya {tagihan.status.value}")
    if jumlah_bayar <= 0 or jumlah_bayar > tagihan.sisa:
        raise JumlahBayarTidakValidError(
            f"Jumlah bayar harus antara 0 dan sisa tagihan ({tagihan.sisa})"
        )

    jenis = db.query(JenisPembayaran).filter(JenisPembayaran.id == tagihan.jenis_pembayaran_id).first()

    header = posting_jurnal(
        db=db,
        departemen_id=tagihan.departemen_id,
        tahun_buku_id=tahun_buku_id,
        tanggal=tanggal,
        keterangan=keterangan or f"Pembayaran tagihan {tagihan.no_tagihan}",
        sumber_modul=SumberModul.PENERIMAAN,
        petugas_id=petugas_id,
        baris=[
            BarisJurnal(akun_id=akun_kas_id, debit=jumlah_bayar),
            BarisJurnal(akun_id=jenis.akun_piutang_id, kredit=jumlah_bayar),
        ],
    )

    pembayaran = PembayaranTagihan(
        tagihan_id=tagihan.id,
        tanggal=tanggal,
        jumlah_bayar=jumlah_bayar,
        akun_kas_id=akun_kas_id,
        petugas_id=petugas_id,
        keterangan=keterangan,
        jurnal_header_id=header.id,
    )
    db.add(pembayaran)
    db.flush()
    header.sumber_id = pembayaran.id

    tagihan.sisa = tagihan.sisa - jumlah_bayar
    if tagihan.sisa <= 0:
        tagihan.status = StatusTagihan.LUNAS

    catat_audit(
        db, tabel="pembayaran_tagihan", record_id=pembayaran.id, aksi=AksiAudit.BUAT, user_id=petugas_id,
        data_baru={"tagihan_id": tagihan.id, "jumlah_bayar": str(jumlah_bayar)},
    )

    return pembayaran
