"""Model Jurnal: JurnalHeader (per transaksi) + JurnalDetail (baris debit/kredit)."""
import enum
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Text, ForeignKey, Enum, Numeric, func
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
    sumber_id = Column(Integer, nullable=True)
    petugas_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(StatusJurnal), default=StatusJurnal.AKTIF, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    departemen = relationship("Departemen")
    tahun_buku = relationship("TahunBuku")
    detail = relationship("JurnalDetail", back_populates="header", cascade="all, delete-orphan")


class JurnalDetail(Base):
    __tablename__ = "jurnal_detail"

    id = Column(Integer, primary_key=True)
    jurnal_header_id = Column(Integer, ForeignKey("jurnal_header.id"), nullable=False)
    akun_id = Column(Integer, ForeignKey("akun.id"), nullable=False)
    debit = Column(Numeric(15, 2), nullable=False, default=0)
    kredit = Column(Numeric(15, 2), nullable=False, default=0)

    header = relationship("JurnalHeader", back_populates="detail")
    akun = relationship("Akun")
