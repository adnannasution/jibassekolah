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


def upgrade() -> None:
    # no_jurnal sebelumnya unique global, padahal penomorannya di-generate
    # per tahun_buku (lihat _generate_no_jurnal di app/core/ledger.py) --
    # ganti jadi unique gabungan (tahun_buku_id, no_jurnal) supaya tahun buku
    # baru tidak bentrok dengan nomor jurnal tahun buku lama. Constraint unique
    # single-column lama tidak bernama eksplisit, jadi dikenali lewat naming
    # convention saat reflect supaya bisa di-drop di semua dialect (termasuk
    # SQLite yang butuh table recreate untuk DROP CONSTRAINT).
    with op.batch_alter_table(
        'jurnal_header', recreate='always', naming_convention=NAMING_CONVENTION
    ) as batch_op:
        batch_op.drop_constraint('uq_jurnal_header_no_jurnal', type_='unique')
        batch_op.create_unique_constraint(
            'uq_jurnal_header_tahun_buku_no_jurnal', ['tahun_buku_id', 'no_jurnal']
        )


def downgrade() -> None:
    with op.batch_alter_table('jurnal_header', recreate='always') as batch_op:
        batch_op.drop_constraint('uq_jurnal_header_tahun_buku_no_jurnal', type_='unique')
        batch_op.create_unique_constraint('uq_jurnal_header_no_jurnal_legacy', ['no_jurnal'])
