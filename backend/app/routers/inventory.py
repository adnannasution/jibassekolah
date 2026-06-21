"""Router modul Inventory: GroupBarang (hierarkis) & Barang. Murni master data
stok barang -- TIDAK ada endpoint yang menyentuh jurnal/ledger sama sekali.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inventory import Barang, GroupBarang
from app.schemas.inventory import (
    BarangCreate,
    BarangOut,
    GroupBarangCreate,
    GroupBarangOut,
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("/group-barang", response_model=List[GroupBarangOut])
def list_group_barang(db: Session = Depends(get_db)):
    return db.query(GroupBarang).order_by(GroupBarang.nama).all()


@router.post("/group-barang", response_model=GroupBarangOut)
def create_group_barang(payload: GroupBarangCreate, db: Session = Depends(get_db)):
    obj = GroupBarang(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/barang", response_model=List[BarangOut])
def list_barang(group_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Barang)
    if group_id is not None:
        query = query.filter(Barang.group_id == group_id)
    return query.order_by(Barang.nama).all()


@router.post("/barang", response_model=BarangOut)
def create_barang(payload: BarangCreate, db: Session = Depends(get_db)):
    obj = Barang(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
