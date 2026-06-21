"""
Modul Inventory: GroupBarang (hierarkis, self-referencing parent) dan Barang
(data barang per group). Modul ini TIDAK menyentuh jurnal/ledger sama sekali
(lihat CLAUDE.md roadmap modul 7) -- murni master data stok barang.
"""
from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class GroupBarang(Base):
    """Group barang hierarkis, mis. "Elektronik" > "Komputer" > "Laptop"."""
    __tablename__ = "group_barang"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("group_barang.id"), nullable=True)
    kode = Column(String(20), nullable=False)
    nama = Column(String(100), nullable=False)
    aktif = Column(Boolean, default=True, nullable=False)

    parent = relationship("GroupBarang", remote_side=[id])

    __table_args__ = (UniqueConstraint("kode", name="uq_group_barang_kode"),)


class Barang(Base):
    __tablename__ = "barang"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("group_barang.id"), nullable=False)
    kode = Column(String(30), nullable=False)
    nama = Column(String(150), nullable=False)
    satuan = Column(String(20), nullable=False)
    stok = Column(Numeric(15, 2), default=0, nullable=False)
    harga_satuan = Column(Numeric(15, 2), nullable=True)
    keterangan = Column(Text, nullable=True)
    aktif = Column(Boolean, default=True, nullable=False)

    group = relationship("GroupBarang")

    __table_args__ = (UniqueConstraint("kode", name="uq_barang_kode"),)
