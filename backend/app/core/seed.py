"""Seed akun admin pertama saat aplikasi start, supaya tidak perlu bikin
user manual lewat /docs tiap kali setup environment baru. Hanya jalan kalau
tabel users masih kosong DAN env var ADMIN_LOGIN/ADMIN_PASSWORD diisi.
"""
import os

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import TingkatPengguna, User


def seed_admin_pertama(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    login = os.getenv("ADMIN_LOGIN")
    password = os.getenv("ADMIN_PASSWORD")
    if not login or not password:
        return

    nama = os.getenv("ADMIN_NAMA", "Administrator")
    db.add(User(
        login=login,
        nama=nama,
        password_hash=hash_password(password),
        tingkat=TingkatPengguna.ADMIN,
    ))
    db.commit()
