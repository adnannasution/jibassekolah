"""Helper kecil untuk mencatat audit_log -- dipakai semua modul yang
melakukan aksi BUAT/EDIT/HAPUS/LOGIN, supaya tidak construct AuditLog(...)
berulang-ulang di tiap call site."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit import AksiAudit, AuditLog


def catat_audit(
    db: Session,
    tabel: str,
    record_id: int,
    aksi: AksiAudit,
    user_id: int,
    data_lama: Optional[dict] = None,
    data_baru: Optional[dict] = None,
    alasan: Optional[str] = None,
) -> None:
    db.add(AuditLog(
        tabel=tabel,
        record_id=record_id,
        aksi=aksi,
        data_lama=data_lama,
        data_baru=data_baru,
        alasan=alasan,
        user_id=user_id,
    ))
