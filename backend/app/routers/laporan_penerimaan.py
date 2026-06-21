"""Router Laporan Penerimaan -- query langsung dari Tagihan/PembayaranTagihan
(beda sumber data dari router laporan.py yang query jurnal_detail)."""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import laporan_penerimaan as laporan_penerimaan_core
from app.database import get_db
from app.schemas.laporan_penerimaan import (
    RekapitulasiPenerimaanBaris, SiswaMenunggakDetailBaris, SiswaMenunggakRekapBaris,
    TagihanPerKelasBaris, TagihanPerSiswaDetailBaris, TagihanRekapPerSiswaBaris,
)

router = APIRouter(prefix="/api/laporan-penerimaan", tags=["laporan-penerimaan"])


@router.get("/per-kelas", response_model=List[TagihanPerKelasBaris])
def get_tagihan_per_kelas(
    tahun_buku_id: int, departemen_id: Optional[int] = None, db: Session = Depends(get_db)
):
    return laporan_penerimaan_core.tagihan_per_kelas(db, tahun_buku_id, departemen_id)


@router.get("/per-siswa", response_model=List[TagihanRekapPerSiswaBaris])
def get_tagihan_rekap_per_siswa(
    tahun_buku_id: int, departemen_id: Optional[int] = None, db: Session = Depends(get_db)
):
    return laporan_penerimaan_core.tagihan_rekap_per_siswa(db, tahun_buku_id, departemen_id)


@router.get("/per-siswa/{siswa_id}", response_model=List[TagihanPerSiswaDetailBaris])
def get_tagihan_per_siswa_detail(siswa_id: int, tahun_buku_id: int, db: Session = Depends(get_db)):
    return laporan_penerimaan_core.tagihan_per_siswa_detail(db, tahun_buku_id, siswa_id)


@router.get("/siswa-menunggak", response_model=List[SiswaMenunggakDetailBaris])
def get_siswa_menunggak_detail(
    tahun_buku_id: int,
    departemen_id: Optional[int] = None,
    kelas_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return laporan_penerimaan_core.siswa_menunggak_detail(db, tahun_buku_id, departemen_id, kelas_id)


@router.get("/siswa-menunggak/rekap", response_model=List[SiswaMenunggakRekapBaris])
def get_siswa_menunggak_rekap(
    tahun_buku_id: int, departemen_id: Optional[int] = None, db: Session = Depends(get_db)
):
    return laporan_penerimaan_core.siswa_menunggak_rekap(db, tahun_buku_id, departemen_id)


@router.get("/rekapitulasi", response_model=List[RekapitulasiPenerimaanBaris])
def get_rekapitulasi_penerimaan(
    tahun_buku_id: int,
    departemen_id: Optional[int] = None,
    tanggal_mulai: Optional[date] = None,
    tanggal_selesai: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return laporan_penerimaan_core.rekapitulasi_penerimaan(
        db, tahun_buku_id, departemen_id, tanggal_mulai, tanggal_selesai
    )
