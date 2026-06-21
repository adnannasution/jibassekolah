"""tambah aksi BUAT dan LOGIN ke audit_log

Revision ID: 3850815060c7
Revises: 13ee0d75e6d5
Create Date: 2026-06-21 13:58:28.769546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3850815060c7'
down_revision = '13ee0d75e6d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # aksi di audit_log adalah native Postgres ENUM (aksiaudit) -- sebelum ini
    # cuma punya EDIT/HAPUS (dipakai pembatalan jurnal/pengeluaran). Modul
    # Log Aktivitas Pengguna butuh BUAT (semua aksi create transaksi/data)
    # dan LOGIN (event login user) supaya "siapa melakukan apa" tercatat
    # lengkap, bukan cuma pembatalan. ALTER TYPE ... ADD VALUE harus pakai
    # op.execute manual karena Alembic autogenerate tidak reliable mendeteksi
    # penambahan value enum.
    op.execute("ALTER TYPE aksiaudit ADD VALUE IF NOT EXISTS 'BUAT'")
    op.execute("ALTER TYPE aksiaudit ADD VALUE IF NOT EXISTS 'LOGIN'")


def downgrade() -> None:
    # Postgres tidak bisa drop satu value dari enum type tanpa rebuild
    # seluruh type (dan kolom yang memakainya) -- terlalu berisiko untuk
    # migration downgrade biasa. Dianggap irreversible.
    pass
