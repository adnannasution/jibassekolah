"""Router modul Laporan Keuangan -- semua endpoint query langsung dari jurnal_detail."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core import laporan as laporan_core
from app.database import get_db
from app.models.audit import AuditLog
from app.schemas.laporan import (
    ArusKasOut, AuditLogOut, BukuBesarBaris, NeracaOut, NeracaPercobaanBaris,
    PerubahanModalOut, RugiLabaOut,
)

router = APIRouter(prefix="/api/laporan", tags=["laporan"])


@router.get("/buku-besar", response_model=List[BukuBesarBaris])
def get_buku_besar(akun_id: int, tahun_buku_id: int, db: Session = Depends(get_db)):
    return laporan_core.buku_besar(db, akun_id, tahun_buku_id)


@router.get("/neraca-percobaan", response_model=List[NeracaPercobaanBaris])
def get_neraca_percobaan(tahun_buku_id: int, db: Session = Depends(get_db)):
    return laporan_core.neraca_percobaan(db, tahun_buku_id)


@router.get("/rugi-laba", response_model=RugiLabaOut)
def get_rugi_laba(tahun_buku_id: int, db: Session = Depends(get_db)):
    return laporan_core.rugi_laba(db, tahun_buku_id)


@router.get("/neraca", response_model=NeracaOut)
def get_neraca(tahun_buku_id: int, db: Session = Depends(get_db)):
    return laporan_core.neraca(db, tahun_buku_id)


@router.get("/perubahan-modal", response_model=PerubahanModalOut)
def get_perubahan_modal(tahun_buku_id: int, db: Session = Depends(get_db)):
    return laporan_core.perubahan_modal(db, tahun_buku_id)


@router.get("/arus-kas", response_model=ArusKasOut)
def get_arus_kas(
    tahun_buku_id: int,
    akun_kas_ids: Optional[List[int]] = Query(default=None),
    db: Session = Depends(get_db),
):
    return laporan_core.arus_kas(db, tahun_buku_id, akun_kas_ids)


@router.get("/audit-log", response_model=List[AuditLogOut])
def get_audit_log(
    tabel: Optional[str] = None,
    record_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if tabel is not None:
        query = query.filter(AuditLog.tabel == tabel)
    if record_id is not None:
        query = query.filter(AuditLog.record_id == record_id)
    return query.order_by(AuditLog.created_at.desc()).all()
