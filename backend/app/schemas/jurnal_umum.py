"""Schema request/response untuk modul Jurnal Umum."""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.ledger import StatusJurnal, SumberModul


class BarisJurnalSchema(BaseModel):
    akun_id: int
    debit: Decimal = Decimal("0")
    kredit: Decimal = Decimal("0")


class JurnalUmumCreate(BaseModel):
    departemen_id: int
    tahun_buku_id: int
    tanggal: date
    keterangan: str
    baris: List[BarisJurnalSchema]


class JurnalDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    akun_id: int
    debit: Decimal
    kredit: Decimal


class JurnalHeaderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    no_jurnal: str
    tanggal: date
    departemen_id: int
    tahun_buku_id: int
    keterangan: str
    sumber_modul: SumberModul
    status: StatusJurnal
    created_at: datetime
    detail: List[JurnalDetailOut] = []


class BatalkanJurnalRequest(BaseModel):
    alasan: str
