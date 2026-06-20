"""
Model Referensi: Departemen, Akun (Chart of Accounts), Tahun Buku.
Ini fondasi yang dipakai semua modul lain.
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, Enum, Boolean, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class KategoriAkun(str, enum.Enum):
    HARTA = "HARTA"
    PIUTANG = "PIUTANG"
    INVENTARIS = "INVENTARIS"
    UTANG = "UTANG"
    MODAL = "MODAL"
    PENDAPATAN = "PENDAPATAN"
    BIAYA = "BIAYA"


class StatusTahunBuku(str, enum.Enum):
    AKTIF = "AKTIF"
    TUTUP = "TUTUP"


class Departemen(Base):
    __tablename__ = "departemen"

    id = Column(Integer, primary_key=True)
    kode = Column(String(20), unique=True, nullable=False)
    nama = Column(String(100), nullable=False)
    aktif = Column(Boolean, default=True, nullable=False)

    tahun_buku = relationship("TahunBuku", back_populates="departemen")


class Akun(Base):
    """Chart of Accounts / Kode Rekening Perkiraan."""
    __tablename__ = "akun"

    id = Column(Integer, primary_key=True)
    kategori = Column(Enum(KategoriAkun), nullable=False)
    kode = Column(String(20), nullable=False)
    nama = Column(String(150), nullable=False)
    keterangan = Column(Text, nullable=True)
    aktif = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("kode", name="uq_akun_kode"),)


class TahunBuku(Base):
    __tablename__ = "tahun_buku"

    id = Column(Integer, primary_key=True)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    tahun_buku = Column(String(20), nullable=False)  # contoh: "2025/2026"
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_selesai = Column(Date, nullable=True)
    awalan_kuitansi = Column(String(20), nullable=False)
    status = Column(Enum(StatusTahunBuku), default=StatusTahunBuku.AKTIF, nullable=False)
    akun_retained_earning_id = Column(Integer, ForeignKey("akun.id"), nullable=True)
    keterangan = Column(Text, nullable=True)

    departemen = relationship("Departemen", back_populates="tahun_buku")
    akun_retained_earning = relationship("Akun")

    __table_args__ = (
        UniqueConstraint("departemen_id", "tahun_buku", name="uq_departemen_tahun_buku"),
    )
