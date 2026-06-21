"""Schema response untuk Dashboard ringkasan."""
from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from app.models.ledger import SumberModul
from app.schemas.laporan_penerimaan import TunggakanPerKelasBaris


class TransaksiTerakhirBaris(BaseModel):
    jurnal_header_id: int
    no_jurnal: str
    tanggal: date
    keterangan: str
    sumber_modul: SumberModul
    total: Decimal


class DashboardRingkasanOut(BaseModel):
    saldo_kas: Decimal
    jumlah_siswa_menunggak: int
    total_tunggakan: Decimal
    transaksi_terakhir: List[TransaksiTerakhirBaris]
    tunggakan_per_kelas: List[TunggakanPerKelasBaris]
