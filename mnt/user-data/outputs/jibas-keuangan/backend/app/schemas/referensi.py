"""Schema (Pydantic) untuk modul Referensi: Departemen, Akun, Tahun Buku, Tutup Buku."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.referensi import KategoriAkun, StatusTahunBuku


# ---------- Departemen ----------
class DepartemenBase(BaseModel):
    kode: str
    nama: str
    aktif: bool = True


class DepartemenCreate(DepartemenBase):
    pass


class DepartemenOut(DepartemenBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Akun (Chart of Accounts) ----------
class AkunBase(BaseModel):
    kategori: KategoriAkun
    kode: str
    nama: str
    keterangan: Optional[str] = None
    aktif: bool = True


class AkunCreate(AkunBase):
    pass


class AkunOut(AkunBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Tahun Buku ----------
class TahunBukuBase(BaseModel):
    departemen_id: int
    tahun_buku: str
    tanggal_mulai: date
    awalan_kuitansi: str
    keterangan: Optional[str] = None


class TahunBukuCreate(TahunBukuBase):
    pass


class TahunBukuOut(TahunBukuBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tanggal_selesai: Optional[date] = None
    status: StatusTahunBuku


# ---------- Tutup Buku ----------
class TutupBukuRequest(BaseModel):
    departemen_id: int
    tahun_buku_lama_id: int
    tahun_buku_baru: str
    tanggal_mulai_baru: date
    awalan_kuitansi_baru: str
    akun_retained_earning_id: int
    keterangan: Optional[str] = None
