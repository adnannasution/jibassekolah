"""Router modul Referensi: Departemen, Akun, Tahun Buku + proses Tutup Buku."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.tutup_buku import tutup_tahun_buku
from app.database import get_db
from app.models.referensi import Akun, Departemen, KategoriAkun, TahunBuku
from app.schemas.referensi import (
    AkunCreate,
    AkunOut,
    DepartemenCreate,
    DepartemenOut,
    TahunBukuCreate,
    TahunBukuOut,
    TutupBukuRequest,
    TutupBukuResponse,
)

router = APIRouter(prefix="/api/referensi", tags=["referensi"])


@router.get("/departemen", response_model=List[DepartemenOut])
def list_departemen(db: Session = Depends(get_db)):
    return db.query(Departemen).order_by(Departemen.nama).all()


@router.post("/departemen", response_model=DepartemenOut)
def create_departemen(payload: DepartemenCreate, db: Session = Depends(get_db)):
    obj = Departemen(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/akun", response_model=List[AkunOut])
def list_akun(kategori: Optional[KategoriAkun] = None, db: Session = Depends(get_db)):
    query = db.query(Akun)
    if kategori is not None:
        query = query.filter(Akun.kategori == kategori)
    return query.order_by(Akun.kode).all()


@router.post("/akun", response_model=AkunOut)
def create_akun(payload: AkunCreate, db: Session = Depends(get_db)):
    obj = Akun(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/tahun-buku", response_model=List[TahunBukuOut])
def list_tahun_buku(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(TahunBuku)
    if departemen_id is not None:
        query = query.filter(TahunBuku.departemen_id == departemen_id)
    return query.order_by(TahunBuku.tanggal_mulai.desc()).all()


@router.post("/tahun-buku", response_model=TahunBukuOut)
def create_tahun_buku(payload: TahunBukuCreate, db: Session = Depends(get_db)):
    obj = TahunBuku(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/tutup-buku", response_model=TutupBukuResponse)
def proses_tutup_buku(payload: TutupBukuRequest, petugas_id: int, db: Session = Depends(get_db)):
    try:
        hasil = tutup_tahun_buku(db, payload, petugas_id)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return TutupBukuResponse(
        tahun_buku_lama_id=hasil["tahun_lama"].id,
        tahun_buku_baru=hasil["tahun_baru"].tahun_buku,
        laba_rugi_tahun_lama=float(hasil["laba_rugi"]),
    )
