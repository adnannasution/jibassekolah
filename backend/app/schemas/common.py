"""Schema generik dipakai lintas modul (pagination, dst)."""
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class HalamanOut(BaseModel, Generic[T]):
    """Response berhalaman: baris pada halaman ini + total seluruh baris
    (sebelum dipotong halaman) supaya frontend bisa hitung jumlah halaman."""

    items: List[T]
    total: int
    halaman: int
    ukuran_halaman: int
