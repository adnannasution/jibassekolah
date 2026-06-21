"""Schema request/response untuk modul Inventory."""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GroupBarangBase(BaseModel):
    parent_id: Optional[int] = None
    kode: str
    nama: str
    aktif: bool = True


class GroupBarangCreate(GroupBarangBase):
    pass


class GroupBarangOut(GroupBarangBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class BarangBase(BaseModel):
    group_id: int
    kode: str
    nama: str
    satuan: str
    stok: Decimal = Decimal("0")
    harga_satuan: Optional[Decimal] = None
    keterangan: Optional[str] = None
    aktif: bool = True


class BarangCreate(BarangBase):
    pass


class BarangOut(BarangBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
