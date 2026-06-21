"""Schema request/response untuk modul Pengeluaran."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.pengeluaran import StatusPengeluaran


class JenisPengeluaranBase(BaseModel):
    departemen_id: int
    kode: str
    nama: str
    akun_kas_id: int
    akun_biaya_id: int
    nominal_default: Optional[Decimal] = None
    aktif: bool = True


class JenisPengeluaranCreate(JenisPengeluaranBase):
    pass


class JenisPengeluaranOut(JenisPengeluaranBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PengeluaranCreate(BaseModel):
    jenis_pengeluaran_id: int
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah: Decimal
    keterangan: Optional[str] = None


class PengeluaranOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    no_kuitansi: str
    jenis_pengeluaran_id: int
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah: Decimal
    status: StatusPengeluaran
    keterangan: Optional[str] = None
    petugas_id: int
    jenis_pengeluaran: Optional[JenisPengeluaranOut] = None


class BatalkanPengeluaranRequest(BaseModel):
    alasan: str
