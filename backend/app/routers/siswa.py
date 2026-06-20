"""Router modul Siswa & Calon Siswa: Kelas, Siswa, Kelompok Calon Siswa, Calon Siswa."""
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.siswa import CalonSiswa, Kelas, KelompokCalonSiswa, Siswa
from app.schemas.siswa import (
    CalonSiswaCreate,
    CalonSiswaOut,
    KelasCreate,
    KelasOut,
    KelompokCalonSiswaCreate,
    KelompokCalonSiswaOut,
    SiswaCreate,
    SiswaOut,
)

router = APIRouter(prefix="/api/siswa", tags=["siswa"])


@router.get("/kelas", response_model=List[KelasOut])
def list_kelas(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Kelas)
    if departemen_id is not None:
        query = query.filter(Kelas.departemen_id == departemen_id)
    return query.order_by(Kelas.angkatan.desc(), Kelas.nama).all()


@router.post("/kelas", response_model=KelasOut)
def create_kelas(payload: KelasCreate, db: Session = Depends(get_db)):
    obj = Kelas(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/siswa", response_model=List[SiswaOut])
def list_siswa(
    departemen_id: Optional[int] = None,
    kelas_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Siswa)
    if departemen_id is not None:
        query = query.filter(Siswa.departemen_id == departemen_id)
    if kelas_id is not None:
        query = query.filter(Siswa.kelas_id == kelas_id)
    return query.order_by(Siswa.nama).all()


@router.post("/siswa", response_model=SiswaOut)
def create_siswa(payload: SiswaCreate, db: Session = Depends(get_db)):
    obj = Siswa(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/kelompok-calon-siswa", response_model=List[KelompokCalonSiswaOut])
def list_kelompok_calon_siswa(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(KelompokCalonSiswa)
    if departemen_id is not None:
        query = query.filter(KelompokCalonSiswa.departemen_id == departemen_id)
    return query.order_by(KelompokCalonSiswa.nama).all()


@router.post("/kelompok-calon-siswa", response_model=KelompokCalonSiswaOut)
def create_kelompok_calon_siswa(payload: KelompokCalonSiswaCreate, db: Session = Depends(get_db)):
    obj = KelompokCalonSiswa(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/calon-siswa", response_model=List[CalonSiswaOut])
def list_calon_siswa(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(CalonSiswa)
    if departemen_id is not None:
        query = query.filter(CalonSiswa.departemen_id == departemen_id)
    return query.order_by(CalonSiswa.tanggal_daftar.desc()).all()


@router.post("/calon-siswa", response_model=CalonSiswaOut)
def create_calon_siswa(payload: CalonSiswaCreate, db: Session = Depends(get_db)):
    obj = CalonSiswa(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
