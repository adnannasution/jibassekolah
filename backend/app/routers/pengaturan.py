"""Router modul Pengaturan: manajemen user & role (admin/manajer/staf),
scoped per departemen. Login di sini masih sederhana (cek login+password,
belum ada session/token) -- cukup untuk MVP karena modul-modul lain belum
punya sistem auth.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import catat_audit
from app.core.security import hash_password, verify_password
from app.database import get_db
from app.models.audit import AksiAudit
from app.models.user import User
from app.schemas.pengaturan import (
    GantiPasswordRequest,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserOut,
    UserUpdate,
)

router = APIRouter(prefix="/api/pengaturan", tags=["pengaturan"])


@router.get("/users", response_model=List[UserOut])
def list_users(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if departemen_id is not None:
        query = query.filter(User.departemen_id == departemen_id)
    return query.order_by(User.nama).all()


@router.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, pelaku_id: int, db: Session = Depends(get_db)):
    if db.query(User).filter(User.login == payload.login).first():
        raise HTTPException(status_code=400, detail=f"Login '{payload.login}' sudah dipakai")
    obj = User(
        login=payload.login,
        nama=payload.nama,
        password_hash=hash_password(payload.password),
        tingkat=payload.tingkat,
        departemen_id=payload.departemen_id,
    )
    db.add(obj)
    db.flush()
    catat_audit(
        db, tabel="users", record_id=obj.id, aksi=AksiAudit.BUAT, user_id=pelaku_id,
        data_baru={"login": obj.login, "nama": obj.nama, "tingkat": obj.tingkat.value},
    )
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, pelaku_id: int, db: Session = Depends(get_db)):
    obj = db.query(User).filter(User.id == user_id).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    data_lama = {"nama": obj.nama, "tingkat": obj.tingkat.value, "aktif": obj.aktif}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    catat_audit(
        db, tabel="users", record_id=obj.id, aksi=AksiAudit.EDIT, user_id=pelaku_id,
        data_lama=data_lama, data_baru={"nama": obj.nama, "tingkat": obj.tingkat.value, "aktif": obj.aktif},
    )
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/users/{user_id}/ganti-password", response_model=UserOut)
def ganti_password(user_id: int, payload: GantiPasswordRequest, pelaku_id: int, db: Session = Depends(get_db)):
    obj = db.query(User).filter(User.id == user_id).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    obj.password_hash = hash_password(payload.password_baru)
    catat_audit(
        db, tabel="users", record_id=obj.id, aksi=AksiAudit.EDIT, user_id=pelaku_id,
        alasan="Ganti password",
    )
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    obj = db.query(User).filter(User.login == payload.login).first()
    if obj is None or not obj.aktif or not verify_password(payload.password, obj.password_hash):
        raise HTTPException(status_code=401, detail="Login atau password salah")
    obj.login_terakhir = datetime.utcnow()
    catat_audit(db, tabel="users", record_id=obj.id, aksi=AksiAudit.LOGIN, user_id=obj.id)
    db.commit()
    db.refresh(obj)
    return LoginResponse(user=obj)
