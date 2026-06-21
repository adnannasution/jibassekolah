"""
Model Pengeluaran: JenisPengeluaran (mapping akun tetap) dan Pengeluaran
(transaksi pembayaran + kuitansi).

Beda dengan Penerimaan, modul ini TIDAK pakai logic akrual -- tiap
jenis_pengeluaran punya mapping tetap rek_kredit (akun kas) & rek_debet
(akun biaya), dan posting langsung Debit Biaya, Kredit Kas saat transaksi
terjadi (lihat CLAUDE.md).
"""
import enum
from sqlalchemy import (
    Column, Integer, String, Date, Text, ForeignKey, Enum, Numeric, Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class StatusPengeluaran(str, enum.Enum):
    AKTIF = "AKTIF"
    DIBATALKAN = "DIBATALKAN"


class JenisPengeluaran(Base):
    __tablename__ = "jenis_pengeluaran"

    id = Column(Integer, primary_key=True)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    kode = Column(String(20), nullable=False)
    nama = Column(String(100), nullable=False)
    akun_kas_id = Column(Integer, ForeignKey("akun.id"), nullable=False)  # rek_kredit
    akun_biaya_id = Column(Integer, ForeignKey("akun.id"), nullable=False)  # rek_debet
    nominal_default = Column(Numeric(15, 2), nullable=True)
    aktif = Column(Boolean, default=True, nullable=False)

    departemen = relationship("Departemen")
    akun_kas = relationship("Akun", foreign_keys=[akun_kas_id])
    akun_biaya = relationship("Akun", foreign_keys=[akun_biaya_id])


class Pengeluaran(Base):
    __tablename__ = "pengeluaran"

    id = Column(Integer, primary_key=True)
    no_kuitansi = Column(String(30), nullable=False)
    jenis_pengeluaran_id = Column(Integer, ForeignKey("jenis_pengeluaran.id"), nullable=False)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    tahun_buku_id = Column(Integer, ForeignKey("tahun_buku.id"), nullable=False)
    tanggal = Column(Date, nullable=False)
    jumlah = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(StatusPengeluaran), default=StatusPengeluaran.AKTIF, nullable=False)
    keterangan = Column(Text, nullable=True)
    petugas_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    jurnal_header_id = Column(Integer, ForeignKey("jurnal_header.id"), nullable=True)

    jenis_pengeluaran = relationship("JenisPengeluaran")
    departemen = relationship("Departemen")
    tahun_buku = relationship("TahunBuku")
    jurnal_header = relationship("JurnalHeader")

    # no_kuitansi digenerate per tahun_buku (lihat _generate_no_kuitansi di
    # app/core/pengeluaran.py) -- unique-nya HARUS digabung dengan
    # tahun_buku_id, bukan global, supaya tahun buku baru tidak bentrok
    # dengan nomor kuitansi tahun buku lama (kasus yang sama pernah jadi
    # bug di no_jurnal, lihat migration 831b724d9486).
    __table_args__ = (
        UniqueConstraint("tahun_buku_id", "no_kuitansi", name="uq_pengeluaran_tahun_buku_no_kuitansi"),
    )
