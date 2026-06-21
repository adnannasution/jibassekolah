"""Schema request/response untuk modul Pengaturan (user & role)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import TingkatPengguna


class UserCreate(BaseModel):
    login: str
    nama: str
    password: str
    tingkat: TingkatPengguna
    departemen_id: Optional[int] = None  # null = akses semua departemen


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    login: str
    nama: str
    tingkat: TingkatPengguna
    departemen_id: Optional[int] = None
    aktif: bool
    login_terakhir: Optional[datetime] = None


class UserUpdate(BaseModel):
    nama: Optional[str] = None
    tingkat: Optional[TingkatPengguna] = None
    departemen_id: Optional[int] = None
    aktif: Optional[bool] = None


class GantiPasswordRequest(BaseModel):
    password_baru: str


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    user: UserOut
