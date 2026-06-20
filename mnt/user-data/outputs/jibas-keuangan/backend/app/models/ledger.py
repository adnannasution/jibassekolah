"""
Mesin Jurnal: jantung sistem akuntansi.
Setiap transaksi (Penerimaan, Pengeluaran, Jurnal Umum) menghasilkan satu
JurnalHeader dengan >=2 baris JurnalDetail yang totalnya harus balance
(total debit == total kredit). Validasi balance dilakukan di app/core/ledger.py,
bukan cuma di sini, supaya tidak ada jalur insert yang melewatinya.
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Date, Numeric, ForeignKey, Enum, Text, DateTime, func
)
from sqlalchemy.orm import relationship

from app.database import Base


class SumberModul(str, enum.Enum):
    PENERIMAAN = "PENERIMAAN"
    PENGELUARAN = "PENGELUARAN"
    JURNAL_UMUM = "JURNAL_UMUM"
    TUTUP_BUKU = "TUTUP_BUKU"


class StatusJurnal(str, enum.Enum):
    AKTIF = "AKTIF"
    DIBATALKAN = "DIBATALKAN"


class JurnalHeader(Base):
    __tablename__ = "jurnal_header"

    id = Column(Integer, primary_key=True)
    no_jurnal = Column(String(30), unique=True, nullable=False)
    tanggal = Column(Date, nullable=False)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    tahun_buku_id = Column(Integer, ForeignKey("tahun_buku.id"), nullable=False)
    keterangan = Column(Text, nullable=False)
    sumber_modul = Column(Enum(SumberModul), nullable=False)
    sumber_id = Column(Integer, nullable=True)  # id baris transaksi asal (penerimaan/pengeluaran)
    petugas_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(StatusJurnal), default=StatusJurnal.AKTIF, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    detail = relationship("JurnalDetail", back_populates="header", cascade="all, delete-orphan")


class JurnalDetail(Base):
    __tablename__ = "jurnal_detail"

    id = Column(Integer, primary_key=True)
    jurnal_header_id = Column(Integer, ForeignKey("jurnal_header.id"), nullable=False)
    akun_id = Column(Integer, ForeignKey("akun.id"), nullable=False)
    debit = Column(Numeric(15, 2), default=0, nullable=False)
    kredit = Column(Numeric(15, 2), default=0, nullable=False)

    header = relationship("JurnalHeader", back_populates="detail")
    akun = relationship("Akun")
