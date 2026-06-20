"""Modul Siswa & Calon Siswa - master data, dipakai modul Penerimaan."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class StatusSiswa(str, enum.Enum):
    AKTIF = "AKTIF"
    LULUS = "LULUS"
    KELUAR = "KELUAR"


class Kelas(Base):
    __tablename__ = "kelas"

    id = Column(Integer, primary_key=True)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    angkatan = Column(String(10), nullable=False)
    tingkat = Column(String(10), nullable=False)
    nama = Column(String(20), nullable=False)  # contoh: "1-A", "XI IPA 1"

    departemen = relationship("Departemen")


class Siswa(Base):
    __tablename__ = "siswa"

    id = Column(Integer, primary_key=True)
    nis = Column(String(30), unique=True, nullable=False)
    nama = Column(String(150), nullable=False)
    kelas_id = Column(Integer, ForeignKey("kelas.id"), nullable=False)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    hp = Column(String(30), nullable=True)
    telepon = Column(String(30), nullable=True)
    alamat = Column(Text, nullable=True)
    foto = Column(String(255), nullable=True)
    status = Column(Enum(StatusSiswa), default=StatusSiswa.AKTIF, nullable=False)

    kelas = relationship("Kelas")
    departemen = relationship("Departemen")


class KelompokCalonSiswa(Base):
    __tablename__ = "kelompok_calon_siswa"

    id = Column(Integer, primary_key=True)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    nama = Column(String(100), nullable=False)  # contoh: "Siswa Jalur NON-PMDK"


class CalonSiswa(Base):
    __tablename__ = "calon_siswa"

    id = Column(Integer, primary_key=True)
    no_registrasi = Column(String(30), unique=True, nullable=False)
    nama = Column(String(150), nullable=False)
    kelompok_id = Column(Integer, ForeignKey("kelompok_calon_siswa.id"), nullable=False)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=False)
    proses = Column(String(50), nullable=True)  # status pendaftaran, contoh: "Pendaftaran (A)"
    hp = Column(String(30), nullable=True)
    alamat = Column(Text, nullable=True)
    foto = Column(String(255), nullable=True)
    tanggal_daftar = Column(Date, nullable=True)

    kelompok = relationship("KelompokCalonSiswa")
    departemen = relationship("Departemen")
