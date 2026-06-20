"""Model Pengguna (modul Pengaturan) - role-based access per departemen."""
import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class TingkatPengguna(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAJER = "MANAJER"
    STAF = "STAF"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    nama = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    tingkat = Column(Enum(TingkatPengguna), nullable=False)
    departemen_id = Column(Integer, ForeignKey("departemen.id"), nullable=True)  # null = semua departemen
    aktif = Column(Boolean, default=True, nullable=False)
    login_terakhir = Column(DateTime, nullable=True)

    departemen = relationship("Departemen")
