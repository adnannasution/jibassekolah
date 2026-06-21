"""Registrasi semua model ke Base.metadata, dipakai Alembic autogenerate."""
from app.models.referensi import Departemen, Akun, TahunBuku, KategoriAkun, StatusTahunBuku  # noqa: F401
from app.models.ledger import JurnalHeader, JurnalDetail, SumberModul, StatusJurnal  # noqa: F401
from app.models.siswa import Kelas, Siswa, KelompokCalonSiswa, CalonSiswa, StatusSiswa  # noqa: F401
from app.models.user import User, TingkatPengguna  # noqa: F401
from app.models.audit import AuditLog, AksiAudit  # noqa: F401
from app.models.penerimaan import (  # noqa: F401
    JenisPembayaran, Tagihan, PembayaranTagihan, StatusTagihan, StatusPembayaran,
)
from app.models.pengeluaran import (  # noqa: F401
    JenisPengeluaran, Pengeluaran, StatusPengeluaran,
)
from app.models.inventory import GroupBarang, Barang  # noqa: F401
