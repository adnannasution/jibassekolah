"""Schema request/response untuk modul Siswa & Calon Siswa."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.siswa import StatusSiswa


class KelasBase(BaseModel):
    departemen_id: int
    angkatan: str
    tingkat: str
    nama: str


class KelasCreate(KelasBase):
    pass


class KelasOut(KelasBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SiswaBase(BaseModel):
    nis: str
    nama: str
    kelas_id: int
    departemen_id: int
    hp: Optional[str] = None
    telepon: Optional[str] = None
    alamat: Optional[str] = None
    foto: Optional[str] = None
    status: StatusSiswa = StatusSiswa.AKTIF


class SiswaCreate(SiswaBase):
    pass


class SiswaOut(SiswaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class KelompokCalonSiswaBase(BaseModel):
    departemen_id: int
    nama: str


class KelompokCalonSiswaCreate(KelompokCalonSiswaBase):
    pass


class KelompokCalonSiswaOut(KelompokCalonSiswaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CalonSiswaBase(BaseModel):
    no_registrasi: str
    nama: str
    kelompok_id: int
    departemen_id: int
    proses: Optional[str] = None
    hp: Optional[str] = None
    alamat: Optional[str] = None
    foto: Optional[str] = None
    tanggal_daftar: Optional[date] = None


class CalonSiswaCreate(CalonSiswaBase):
    pass


class CalonSiswaOut(CalonSiswaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
