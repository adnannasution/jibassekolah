"""Schema response untuk Laporan Penerimaan (per kelas, per siswa, siswa
menunggak, rekapitulasi). Mengikuti style schemas/laporan.py."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.penerimaan import StatusTagihan


class TagihanPerKelasBaris(BaseModel):
    kelas_id: int
    kelas_nama: str
    tingkat: str
    total_tagihan: Decimal
    total_diskon: Decimal
    total_sisa: Decimal
    jumlah_tagihan: int


class TagihanPerSiswaDetailBaris(BaseModel):
    tagihan_id: int
    no_tagihan: str
    tanggal: date
    jenis_pembayaran_nama: str
    jumlah_tagihan: Decimal
    diskon: Decimal
    sisa: Decimal
    status: StatusTagihan


class TagihanRekapPerSiswaBaris(BaseModel):
    siswa_id: int
    nis: str
    nama: str
    kelas_nama: str
    total_tagihan: Decimal
    total_diskon: Decimal
    total_sisa: Decimal


class SiswaMenunggakDetailBaris(BaseModel):
    tagihan_id: int
    no_tagihan: str
    tanggal: date
    siswa_id: int
    siswa_nama: str
    siswa_nis: str
    kelas_nama: str
    jenis_pembayaran_nama: str
    sisa: Decimal


class SiswaMenunggakRekapBaris(BaseModel):
    siswa_id: int
    nis: str
    nama: str
    kelas_nama: str
    total_sisa: Decimal
    jumlah_tagihan_menunggak: int


class TunggakanPerKelasBaris(BaseModel):
    kelas_id: int
    kelas_nama: str
    total_sisa: Decimal


class RekapitulasiPenerimaanBaris(BaseModel):
    jenis_pembayaran_id: int
    jenis_pembayaran_nama: Optional[str] = None
    total_ditagihkan: Decimal
    total_diterima: Decimal
