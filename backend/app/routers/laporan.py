"""Router modul Laporan Keuangan -- semua endpoint query langsung dari jurnal_detail."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core import laporan as laporan_core
from app.database import get_db
from app.models.audit import AuditLog
from app.schemas.common import HalamanOut
from app.schemas.laporan import (
    ArusKasOut, AuditLogOut, BukuBesarBaris, NeracaOut, NeracaPercobaanBaris,
    PerubahanModalOut, RugiLabaOut,
)

router = APIRouter(prefix="/api/laporan", tags=["laporan"])


@router.get("/buku-besar", response_model=HalamanOut[BukuBesarBaris])
def get_buku_besar(
    akun_id: int,
    tahun_buku_id: int,
    cari: Optional[str] = None,
    halaman: int = 1,
    ukuran_halaman: int = 20,
    db: Session = Depends(get_db),
):
    # Saldo berjalan harus dihitung dari urutan penuh sebelum dipotong halaman,
    # jadi pagination & search dilakukan di sini (Python), bukan di SQL.
    semua = laporan_core.buku_besar(db, akun_id, tahun_buku_id)
    if cari:
        kata = cari.lower()
        semua = [b for b in semua if kata in b["no_jurnal"].lower() or kata in b["keterangan"].lower()]
    total = len(semua)
    mulai = (halaman - 1) * ukuran_halaman
    return {
        "items": semua[mulai : mulai + ukuran_halaman],
        "total": total,
        "halaman": halaman,
        "ukuran_halaman": ukuran_halaman,
    }


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


@router.get("/audit-log", response_model=HalamanOut[AuditLogOut])
def get_audit_log(
    tabel: Optional[str] = None,
    record_id: Optional[int] = None,
    cari: Optional[str] = None,
    halaman: int = 1,
    ukuran_halaman: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if tabel is not None:
        query = query.filter(AuditLog.tabel == tabel)
    if record_id is not None:
        query = query.filter(AuditLog.record_id == record_id)
    if cari:
        kata = f"%{cari}%"
        query = query.filter(or_(AuditLog.tabel.ilike(kata), AuditLog.alasan.ilike(kata)))

    total = query.count()
    rows = (
        query.order_by(AuditLog.created_at.desc())
        .offset((halaman - 1) * ukuran_halaman)
        .limit(ukuran_halaman)
        .all()
    )
    return {"items": rows, "total": total, "halaman": halaman, "ukuran_halaman": ukuran_halaman}
