"""Router modul Pengeluaran: Jenis Pengeluaran, Pengeluaran."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.ledger import JurnalTidakBalanceError, TahunBukuTutupError
from app.core.pengeluaran import (
    BuatPengeluaranRequest, PengeluaranSudahDibatalkanError,
    batalkan_pengeluaran, buat_pengeluaran,
)
from app.database import get_db
from app.models.pengeluaran import JenisPengeluaran, Pengeluaran
from app.schemas.pengeluaran import (
    BatalkanPengeluaranRequest, JenisPengeluaranCreate, JenisPengeluaranOut,
    PengeluaranCreate, PengeluaranOut,
)

router = APIRouter(prefix="/api/pengeluaran", tags=["pengeluaran"])


@router.get("/jenis-pengeluaran", response_model=List[JenisPengeluaranOut])
def list_jenis_pengeluaran(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(JenisPengeluaran)
    if departemen_id is not None:
        query = query.filter(JenisPengeluaran.departemen_id == departemen_id)
    return query.order_by(JenisPengeluaran.nama).all()


@router.post("/jenis-pengeluaran", response_model=JenisPengeluaranOut)
def create_jenis_pengeluaran(payload: JenisPengeluaranCreate, db: Session = Depends(get_db)):
    obj = JenisPengeluaran(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/pengeluaran", response_model=List[PengeluaranOut])
def list_pengeluaran(
    departemen_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Pengeluaran)
    if departemen_id is not None:
        query = query.filter(Pengeluaran.departemen_id == departemen_id)
    if status is not None:
        query = query.filter(Pengeluaran.status == status)
    return query.order_by(Pengeluaran.tanggal.desc()).all()


@router.post("/pengeluaran", response_model=PengeluaranOut)
def create_pengeluaran(payload: PengeluaranCreate, petugas_id: int, db: Session = Depends(get_db)):
    try:
        pengeluaran = buat_pengeluaran(db, BuatPengeluaranRequest(**payload.model_dump()), petugas_id)
    except (JurnalTidakBalanceError, TahunBukuTutupError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(pengeluaran)
    return pengeluaran


@router.post("/pengeluaran/{pengeluaran_id}/batalkan", response_model=PengeluaranOut)
def cancel_pengeluaran(
    pengeluaran_id: int, payload: BatalkanPengeluaranRequest, user_id: int, db: Session = Depends(get_db),
):
    try:
        pengeluaran = batalkan_pengeluaran(db, pengeluaran_id, payload.alasan, user_id)
    except (TahunBukuTutupError, PengeluaranSudahDibatalkanError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(pengeluaran)
    return pengeluaran
