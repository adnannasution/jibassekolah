"""Schema response untuk modul Laporan Keuangan."""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.models.audit import AksiAudit
from app.models.referensi import KategoriAkun


class BukuBesarBaris(BaseModel):
    tanggal: date
    no_jurnal: str
    keterangan: str
    debit: Decimal
    kredit: Decimal
    saldo: Decimal


class NeracaPercobaanBaris(BaseModel):
    akun_id: int
    kode: str
    nama: str
    kategori: KategoriAkun
    total_debit: Decimal
    total_kredit: Decimal
    saldo: Decimal


class SaldoAkunBaris(BaseModel):
    akun_id: int
    kode: str
    nama: str
    debit: Decimal
    kredit: Decimal
    saldo: Decimal


class RugiLabaOut(BaseModel):
    pendapatan: List[SaldoAkunBaris]
    biaya: List[SaldoAkunBaris]
    total_pendapatan: Decimal
    total_biaya: Decimal
    laba_rugi: Decimal


class NeracaOut(BaseModel):
    aset: List[SaldoAkunBaris]
    liabilitas: List[SaldoAkunBaris]
    modal: List[SaldoAkunBaris]
    laba_rugi_periode: Decimal
    total_aset: Decimal
    total_liabilitas: Decimal
    total_modal: Decimal
    balance: bool


class PerubahanModalOut(BaseModel):
    modal_awal: Decimal
    laba_rugi_periode: Decimal
    modal_akhir: Decimal


class ArusKasBaris(BaseModel):
    akun_id: int
    kode: str
    nama: str
    kas_masuk: Decimal
    kas_keluar: Decimal
    mutasi_bersih: Decimal


class ArusKasOut(BaseModel):
    akun: List[ArusKasBaris]
    total_mutasi_bersih: Decimal


class AuditLogOut(BaseModel):
    id: int
    tabel: str
    record_id: int
    aksi: AksiAudit
    data_lama: Optional[dict] = None
    data_baru: Optional[dict] = None
    alasan: Optional[str] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
