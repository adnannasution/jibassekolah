"""Router modul Jurnal Umum: input manual baris jurnal + pembatalan."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.jurnal_umum import (
    BuatJurnalUmumRequest, JurnalSudahDibatalkanError, batalkan_jurnal_umum, buat_jurnal_umum,
)
from app.core.ledger import BarisJurnal, JurnalTidakBalanceError, TahunBukuTutupError
from app.database import get_db
from app.models.ledger import JurnalHeader
from app.schemas.jurnal_umum import BatalkanJurnalRequest, JurnalHeaderOut, JurnalUmumCreate

router = APIRouter(prefix="/api/jurnal-umum", tags=["jurnal-umum"])


@router.get("/jurnal", response_model=List[JurnalHeaderOut])
def list_jurnal(
    departemen_id: Optional[int] = None,
    tahun_buku_id: Optional[int] = None,
    sumber_modul: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(JurnalHeader)
    if departemen_id is not None:
        query = query.filter(JurnalHeader.departemen_id == departemen_id)
    if tahun_buku_id is not None:
        query = query.filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
    if sumber_modul is not None:
        query = query.filter(JurnalHeader.sumber_modul == sumber_modul)
    return query.order_by(JurnalHeader.tanggal.desc()).all()


@router.post("/jurnal", response_model=JurnalHeaderOut)
def create_jurnal(payload: JurnalUmumCreate, petugas_id: int, db: Session = Depends(get_db)):
    try:
        header = buat_jurnal_umum(
            db,
            BuatJurnalUmumRequest(
                departemen_id=payload.departemen_id,
                tahun_buku_id=payload.tahun_buku_id,
                tanggal=payload.tanggal,
                keterangan=payload.keterangan,
                baris=[BarisJurnal(akun_id=b.akun_id, debit=b.debit, kredit=b.kredit) for b in payload.baris],
            ),
            petugas_id,
        )
    except (JurnalTidakBalanceError, TahunBukuTutupError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(header)
    return header


@router.post("/jurnal/{jurnal_header_id}/batalkan", response_model=JurnalHeaderOut)
def cancel_jurnal(
    jurnal_header_id: int, payload: BatalkanJurnalRequest, user_id: int, db: Session = Depends(get_db),
):
    try:
        header = batalkan_jurnal_umum(db, jurnal_header_id, payload.alasan, user_id)
    except (TahunBukuTutupError, JurnalSudahDibatalkanError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(header)
    return header
