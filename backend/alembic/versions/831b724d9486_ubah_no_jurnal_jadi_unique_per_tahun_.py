"""ubah no_jurnal jadi unique per tahun buku

Revision ID: 831b724d9486
Revises: 39ebca058fb7
Create Date: 2026-06-21 06:17:37.532202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '831b724d9486'
down_revision = '39ebca058fb7'
branch_labels = None
depends_on = None


NAMING_CONVENTION = {"uq": "uq_%(table_name)s_%(column_0_name)s"}


def _nama_constraint_unik_no_jurnal(conn) -> str | None:
    """Cari nama constraint unique lama pada kolom no_jurnal -- namanya beda-beda
    tergantung dialect (Postgres auto-generate "jurnal_header_no_jurnal_key",
    SQLite reflect tanpa nama eksplisit)."""
    inspector = sa.inspect(conn)
    for uc in inspector.get_unique_constraints('jurnal_header'):
        if uc['column_names'] == ['no_jurnal']:
            return uc['name']
    return None


def upgrade() -> None:
    # no_jurnal sebelumnya unique global, padahal penomorannya di-generate
    # per tahun_buku (lihat _generate_no_jurnal di app/core/ledger.py) --
    # ganti jadi unique gabungan (tahun_buku_id, no_jurnal) supaya tahun buku
    # baru tidak bentrok dengan nomor jurnal tahun buku lama. Nama constraint
    # unique lama berbeda per dialect (Postgres auto-generate, SQLite kadang
    # tanpa nama), jadi dicari lewat inspector dulu sebelum di-drop.
    # recreate='auto' (bukan 'always') -- SQLite butuh table recreate untuk
    # DROP CONSTRAINT, tapi Postgres bisa ALTER TABLE langsung; recreate paksa
    # di Postgres gagal karena FK dari tagihan/pembayaran_tagihan/jurnal_detail
    # bergantung ke primary key jurnal_header.
    conn = op.get_bind()
    nama_lama = _nama_constraint_unik_no_jurnal(conn)
    with op.batch_alter_table(
        'jurnal_header', naming_convention=NAMING_CONVENTION
    ) as batch_op:
        if nama_lama:
            batch_op.drop_constraint(nama_lama, type_='unique')
        batch_op.create_unique_constraint(
            'uq_jurnal_header_tahun_buku_no_jurnal', ['tahun_buku_id', 'no_jurnal']
        )


def downgrade() -> None:
    with op.batch_alter_table('jurnal_header') as batch_op:
        batch_op.drop_constraint('uq_jurnal_header_tahun_buku_no_jurnal', type_='unique')
        batch_op.create_unique_constraint('uq_jurnal_header_no_jurnal_legacy', ['no_jurnal'])
