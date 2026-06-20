"""
Proses Tutup Tahun Buku.
1. Hitung laba/rugi tahun buku yang akan ditutup (Pendapatan - Biaya).
2. Posting jurnal penutup: pindahkan laba/rugi ke akun Retained Earning.
3. Tandai tahun buku lama sebagai TUTUP (terkunci, tidak bisa diposting lagi).
4. Buat tahun buku baru berstatus AKTIF.

Catatan implementasi: secara akuntansi yang lebih baku, penutupan akun
nominal (Pendapatan/Biaya) seharusnya lewat akun perantara "Ikhtisar Laba
Rugi" sebelum masuk Retained Earning. Versi ini menyederhanakan dengan
posting langsung ke akun Modal sebagai lawan Retained Earning -- cukup
untuk MVP, bisa disempurnakan kalau modul ini dikembangkan lebih lanjut.
"""
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.ledger import BarisJurnal, posting_jurnal
from app.models.ledger import JurnalDetail, JurnalHeader, StatusJurnal, SumberModul
from app.models.referensi import Akun, KategoriAkun, StatusTahunBuku, TahunBuku


def _hitung_laba_rugi(db: Session, tahun_buku_id: int) -> Decimal:
    """Laba/rugi = (kredit-debit) akun Pendapatan dikurangi (debit-kredit) akun Biaya."""
    rows = (
        db.query(Akun.kategori, func.sum(JurnalDetail.debit), func.sum(JurnalDetail.kredit))
        .join(JurnalDetail, JurnalDetail.akun_id == Akun.id)
        .join(JurnalHeader, JurnalHeader.id == JurnalDetail.jurnal_header_id)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
        .filter(JurnalHeader.status == StatusJurnal.AKTIF)
        .filter(Akun.kategori.in_([KategoriAkun.PENDAPATAN, KategoriAkun.BIAYA]))
        .group_by(Akun.kategori)
        .all()
    )
    pendapatan = Decimal("0")
    biaya = Decimal("0")
    for kategori, debit, kredit in rows:
        debit = debit or Decimal("0")
        kredit = kredit or Decimal("0")
        if kategori == KategoriAkun.PENDAPATAN:
            pendapatan = kredit - debit
        elif kategori == KategoriAkun.BIAYA:
            biaya = debit - kredit
    return pendapatan - biaya


def tutup_tahun_buku(db: Session, request, petugas_id: int) -> dict:
    tahun_lama = db.query(TahunBuku).filter(TahunBuku.id == request.tahun_buku_lama_id).first()
    if tahun_lama is None:
        raise ValueError("Tahun buku lama tidak ditemukan")
    if tahun_lama.status == StatusTahunBuku.TUTUP:
        raise ValueError("Tahun buku ini sudah ditutup sebelumnya")

    laba_rugi = _hitung_laba_rugi(db, tahun_lama.id)

    if laba_rugi != 0:
        akun_modal = db.query(Akun).filter(Akun.kategori == KategoriAkun.MODAL).first()
        if akun_modal is None:
            raise ValueError("Belum ada akun kategori MODAL untuk lawan jurnal penutup")

        baris = [
            BarisJurnal(
                akun_id=request.akun_retained_earning_id,
                debit=Decimal("0") if laba_rugi >= 0 else abs(laba_rugi),
                kredit=laba_rugi if laba_rugi >= 0 else Decimal("0"),
            ),
            BarisJurnal(
                akun_id=akun_modal.id,
                debit=laba_rugi if laba_rugi >= 0 else Decimal("0"),
                kredit=Decimal("0") if laba_rugi >= 0 else abs(laba_rugi),
            ),
        ]
        posting_jurnal(
            db=db,
            departemen_id=tahun_lama.departemen_id,
            tahun_buku_id=tahun_lama.id,
            tanggal=request.tanggal_mulai_baru,
            keterangan=f"Jurnal penutup tahun buku {tahun_lama.tahun_buku}",
            sumber_modul=SumberModul.TUTUP_BUKU,
            petugas_id=petugas_id,
            baris=baris,
        )

    tahun_lama.status = StatusTahunBuku.TUTUP
    tahun_lama.tanggal_selesai = request.tanggal_mulai_baru
    tahun_lama.akun_retained_earning_id = request.akun_retained_earning_id

    tahun_baru = TahunBuku(
        departemen_id=request.departemen_id,
        tahun_buku=request.tahun_buku_baru,
        tanggal_mulai=request.tanggal_mulai_baru,
        awalan_kuitansi=request.awalan_kuitansi_baru,
        status=StatusTahunBuku.AKTIF,
        keterangan=request.keterangan,
    )
    db.add(tahun_baru)
    db.flush()

    return {"tahun_lama": tahun_lama, "tahun_baru": tahun_baru, "laba_rugi": laba_rugi}
