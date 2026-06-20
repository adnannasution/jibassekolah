"""
Import semua model di sini supaya Base.metadata mengenali semua tabel.
Wajib di-import (walau "unused") biar Alembic autogenerate & create_all jalan benar.
"""
from app.models.referensi import Departemen, Akun, TahunBuku  # noqa: F401
from app.models.ledger import JurnalHeader, JurnalDetail  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.siswa import Kelas, Siswa, KelompokCalonSiswa, CalonSiswa  # noqa: F401
