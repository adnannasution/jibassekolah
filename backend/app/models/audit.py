"""
Audit trail generik. Dipakai semua modul yang butuh jejak perubahan
(Laporan Audit Perubahan Data Keuangan di buku manual).
Data lama/baru disimpan sebagai JSON snapshot baris yang diubah/dihapus.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON, Enum
import enum

from app.database import Base


class AksiAudit(str, enum.Enum):
    EDIT = "EDIT"
    HAPUS = "HAPUS"


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    tabel = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    aksi = Column(Enum(AksiAudit), nullable=False)
    data_lama = Column(JSON, nullable=True)
    data_baru = Column(JSON, nullable=True)
    alasan = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
