"""Schema request/response untuk modul Penerimaan."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.penerimaan import StatusPembayaran, StatusTagihan


class JenisPembayaranBase(BaseModel):
    departemen_id: int
    kode: str
    nama: str
    akun_piutang_id: int
    akun_pendapatan_id: int
    nominal_default: Optional[Decimal] = None
    aktif: bool = True


class JenisPembayaranCreate(JenisPembayaranBase):
    pass


class JenisPembayaranOut(JenisPembayaranBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TagihanCreate(BaseModel):
    siswa_id: int
    jenis_pembayaran_id: int
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah_tagihan: Decimal
    diskon: Decimal = Decimal("0")
    langsung_lunas: bool = False
    akun_kas_id: Optional[int] = None
    keterangan: Optional[str] = None


class TagihanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    no_tagihan: str
    siswa_id: int
    jenis_pembayaran_id: int
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah_tagihan: Decimal
    diskon: Decimal
    sisa: Decimal
    status: StatusTagihan
    keterangan: Optional[str] = None


class PembayaranTagihanCreate(BaseModel):
    tagihan_id: int
    tahun_buku_id: int
    tanggal: date
    jumlah_bayar: Decimal
    akun_kas_id: int
    keterangan: Optional[str] = None


class PembayaranTagihanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tagihan_id: int
    tanggal: date
    jumlah_bayar: Decimal
    akun_kas_id: int
    petugas_id: int
    status: StatusPembayaran
    keterangan: Optional[str] = None
