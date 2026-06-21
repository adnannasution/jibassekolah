"""Router modul Penerimaan: Jenis Pembayaran, Tagihan, Pembayaran Tagihan."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.ledger import JurnalTidakBalanceError, TahunBukuTutupError
from app.core.penerimaan import (
    BuatTagihanRequest, JumlahBayarTidakValidError, TagihanSudahLunasError,
    bayar_tagihan, buat_tagihan,
)
from app.database import get_db
from app.models.penerimaan import JenisPembayaran, PembayaranTagihan, Tagihan
from app.schemas.penerimaan import (
    JenisPembayaranCreate, JenisPembayaranOut, PembayaranTagihanCreate,
    PembayaranTagihanOut, TagihanCreate, TagihanOut,
)

router = APIRouter(prefix="/api/penerimaan", tags=["penerimaan"])


@router.get("/jenis-pembayaran", response_model=List[JenisPembayaranOut])
def list_jenis_pembayaran(departemen_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(JenisPembayaran)
    if departemen_id is not None:
        query = query.filter(JenisPembayaran.departemen_id == departemen_id)
    return query.order_by(JenisPembayaran.nama).all()


@router.post("/jenis-pembayaran", response_model=JenisPembayaranOut)
def create_jenis_pembayaran(payload: JenisPembayaranCreate, db: Session = Depends(get_db)):
    obj = JenisPembayaran(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/tagihan", response_model=List[TagihanOut])
def list_tagihan(
    siswa_id: Optional[int] = None,
    departemen_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Tagihan)
    if siswa_id is not None:
        query = query.filter(Tagihan.siswa_id == siswa_id)
    if departemen_id is not None:
        query = query.filter(Tagihan.departemen_id == departemen_id)
    if status is not None:
        query = query.filter(Tagihan.status == status)
    return query.order_by(Tagihan.tanggal.desc()).all()


@router.post("/tagihan", response_model=TagihanOut)
def create_tagihan(payload: TagihanCreate, petugas_id: int, db: Session = Depends(get_db)):
    try:
        tagihan = buat_tagihan(db, BuatTagihanRequest(**payload.model_dump()), petugas_id)
    except (JurnalTidakBalanceError, TahunBukuTutupError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(tagihan)
    return tagihan


@router.get("/pembayaran", response_model=List[PembayaranTagihanOut])
def list_pembayaran(tagihan_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(PembayaranTagihan)
    if tagihan_id is not None:
        query = query.filter(PembayaranTagihan.tagihan_id == tagihan_id)
    return query.order_by(PembayaranTagihan.tanggal.desc()).all()


@router.post("/pembayaran", response_model=PembayaranTagihanOut)
def create_pembayaran(payload: PembayaranTagihanCreate, petugas_id: int, db: Session = Depends(get_db)):
    try:
        pembayaran = bayar_tagihan(
            db,
            tagihan_id=payload.tagihan_id,
            tahun_buku_id=payload.tahun_buku_id,
            tanggal=payload.tanggal,
            jumlah_bayar=payload.jumlah_bayar,
            akun_kas_id=payload.akun_kas_id,
            petugas_id=petugas_id,
            keterangan=payload.keterangan,
        )
    except (JurnalTidakBalanceError, TahunBukuTutupError, TagihanSudahLunasError,
            JumlahBayarTidakValidError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(pembayaran)
    return pembayaran
