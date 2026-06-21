"""
Model Penerimaan: Jenis Pembayaran (mapping akun), Tagihan (piutang diakui di
muka), dan Pembayaran Tagihan (cicilan/lunas).

Keputusan desain diskon (lihat CLAUDE.md): diskon mengurangi nominal piutang
& pendapatan yang diakui langsung saat tagihan dibuat (net = jumlah_tagihan -
diskon). Tidak ada akun "Potongan" terpisah -- lebih sederhana dan konsisten
untuk MVP, karena nilai piutang yang tersisa untuk siswa selalu sama dengan
yang akan benar-benar ditagihkan.
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Date, Text, ForeignKey, Enum, Numeric, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


class StatusTagihan(str, enum.Enum):
    BELUM_LUNAS = "BELUM_LUNAS"
    LUNAS = "LUNAS"
    DIBATALKAN = "DIBATALKAN"


class StatusPembayaran(str, enum.Enum):
    AKTIF = "AKTIF"
    DIBATALKAN = "DIBATALKAN"


class JenisPembayaran(Base):
    """Mapping tetap per jenis pembayaran (mis. SPP, Uang Gedung) ke akun."""
    __tablename__ = "jenis_pembayaran"

    id = Column(Integer, primary_key=True)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    kode = Column(String(20), nullable=False)
    nama = Column(String(100), nullable=False)
    akun_piutang_id = Column(Integer, ForeignKey("akun.id"), nullable=False)
    akun_pendapatan_id = Column(Integer, ForeignKey("akun.id"), nullable=False)
    nominal_default = Column(Numeric(15, 2), nullable=True)
    aktif = Column(Boolean, default=True, nullable=False)

    departemen = relationship("Departemen")
    akun_piutang = relationship("Akun", foreign_keys=[akun_piutang_id])
    akun_pendapatan = relationship("Akun", foreign_keys=[akun_pendapatan_id])


class Tagihan(Base):
    """
    Tagihan ke siswa. Saat dibuat, pendapatan SUDAH diakui penuh (akrual):
    Debit Piutang, Kredit Pendapatan sebesar (jumlah_tagihan - diskon).
    Kalau langsung_lunas=True, tidak ada Piutang sama sekali -- posting
    langsung Debit Kas, Kredit Pendapatan (lihat app/core/penerimaan.py).
    """
    __tablename__ = "tagihan"

    id = Column(Integer, primary_key=True)
    no_tagihan = Column(String(30), unique=True, nullable=False)
    siswa_id = Column(Integer, ForeignKey("siswa.id"), nullable=False)
    jenis_pembayaran_id = Column(Integer, ForeignKey("jenis_pembayaran.id"), nullable=False)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    tahun_buku_id = Column(Integer, ForeignKey("tahun_buku.id"), nullable=False)
    tanggal = Column(Date, nullable=False)
    jumlah_tagihan = Column(Numeric(15, 2), nullable=False)
    diskon = Column(Numeric(15, 2), nullable=False, default=0)
    sisa = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(StatusTagihan), default=StatusTagihan.BELUM_LUNAS, nullable=False)
    keterangan = Column(Text, nullable=True)
    jurnal_header_id = Column(Integer, ForeignKey("jurnal_header.id"), nullable=True)

    siswa = relationship("Siswa")
    jenis_pembayaran = relationship("JenisPembayaran")
    departemen = relationship("Departemen")
    tahun_buku = relationship("TahunBuku")
    jurnal_header = relationship("JurnalHeader")
    pembayaran = relationship("PembayaranTagihan", back_populates="tagihan")


class PembayaranTagihan(Base):
    """Satu baris pelunasan/cicilan untuk sebuah Tagihan: Debit Kas, Kredit Piutang."""
    __tablename__ = "pembayaran_tagihan"

    id = Column(Integer, primary_key=True)
    tagihan_id = Column(Integer, ForeignKey("tagihan.id"), nullable=False)
    tanggal = Column(Date, nullable=False)
    jumlah_bayar = Column(Numeric(15, 2), nullable=False)
    akun_kas_id = Column(Integer, ForeignKey("akun.id"), nullable=False)
    petugas_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(StatusPembayaran), default=StatusPembayaran.AKTIF, nullable=False)
    keterangan = Column(Text, nullable=True)
    jurnal_header_id = Column(Integer, ForeignKey("jurnal_header.id"), nullable=True)

    tagihan = relationship("Tagihan", back_populates="pembayaran")
    akun_kas = relationship("Akun")
    jurnal_header = relationship("JurnalHeader")
