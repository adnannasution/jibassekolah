"""
Logic Laporan Keuangan. SEMUA laporan di sini query langsung dari
jurnal_detail/jurnal_header -- tidak ada tabel hasil hitung terpisah, supaya
laporan selalu akurat tanpa proses sinkronisasi (lihat CLAUDE.md modul 6).

Semua laporan di-scope per tahun_buku_id dan hanya menghitung jurnal
berstatus AKTIF (jurnal yang DIBATALKAN dikecualikan).
"""
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ledger import JurnalDetail, JurnalHeader, StatusJurnal
from app.models.referensi import Akun, KategoriAkun

KATEGORI_ASET = (KategoriAkun.HARTA, KategoriAkun.PIUTANG, KategoriAkun.INVENTARIS)


def buku_besar(db: Session, akun_id: int, tahun_buku_id: int) -> list[dict]:
    """Mutasi satu akun, urut tanggal, dengan saldo berjalan (mulai dari 0
    di awal tahun_buku -- saldo awal tahun buku baru sudah dibawa lewat
    jurnal penutup tutup_buku.py ke akun Retained Earning/Modal)."""
    rows = (
        db.query(JurnalHeader.tanggal, JurnalHeader.no_jurnal, JurnalHeader.keterangan,
                  JurnalDetail.debit, JurnalDetail.kredit)
        .join(JurnalDetail, JurnalDetail.jurnal_header_id == JurnalHeader.id)
        .filter(JurnalDetail.akun_id == akun_id)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
        .filter(JurnalHeader.status == StatusJurnal.AKTIF)
        .order_by(JurnalHeader.tanggal, JurnalHeader.id)
        .all()
    )
    saldo = Decimal("0")
    hasil = []
    for tanggal, no_jurnal, keterangan, debit, kredit in rows:
        saldo += debit - kredit
        hasil.append({
            "tanggal": tanggal, "no_jurnal": no_jurnal, "keterangan": keterangan,
            "debit": debit, "kredit": kredit, "saldo": saldo,
        })
    return hasil


def neraca_percobaan(db: Session, tahun_buku_id: int) -> list[dict]:
    """Trial balance: tiap akun yang punya mutasi di tahun buku ini, total debit/kredit/saldo."""
    rows = (
        db.query(Akun.id, Akun.kode, Akun.nama, Akun.kategori,
                  func.coalesce(func.sum(JurnalDetail.debit), 0),
                  func.coalesce(func.sum(JurnalDetail.kredit), 0))
        .join(JurnalDetail, JurnalDetail.akun_id == Akun.id)
        .join(JurnalHeader, JurnalHeader.id == JurnalDetail.jurnal_header_id)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
        .filter(JurnalHeader.status == StatusJurnal.AKTIF)
        .group_by(Akun.id, Akun.kode, Akun.nama, Akun.kategori)
        .order_by(Akun.kode)
        .all()
    )
    hasil = []
    for akun_id, kode, nama, kategori, total_debit, total_kredit in rows:
        hasil.append({
            "akun_id": akun_id, "kode": kode, "nama": nama, "kategori": kategori,
            "total_debit": total_debit, "total_kredit": total_kredit,
            "saldo": total_debit - total_kredit,
        })
    return hasil


def _saldo_per_kategori(db: Session, tahun_buku_id: int, kategori: tuple) -> list[dict]:
    rows = (
        db.query(Akun.id, Akun.kode, Akun.nama,
                  func.coalesce(func.sum(JurnalDetail.debit), 0),
                  func.coalesce(func.sum(JurnalDetail.kredit), 0))
        .join(JurnalDetail, JurnalDetail.akun_id == Akun.id)
        .join(JurnalHeader, JurnalHeader.id == JurnalDetail.jurnal_header_id)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
        .filter(JurnalHeader.status == StatusJurnal.AKTIF)
        .filter(Akun.kategori.in_(kategori))
        .group_by(Akun.id, Akun.kode, Akun.nama)
        .order_by(Akun.kode)
        .all()
    )
    return [
        {"akun_id": a_id, "kode": kode, "nama": nama, "debit": d, "kredit": k}
        for a_id, kode, nama, d, k in rows
    ]


def rugi_laba(db: Session, tahun_buku_id: int) -> dict:
    pendapatan = _saldo_per_kategori(db, tahun_buku_id, (KategoriAkun.PENDAPATAN,))
    biaya = _saldo_per_kategori(db, tahun_buku_id, (KategoriAkun.BIAYA,))
    for p in pendapatan:
        p["saldo"] = p["kredit"] - p["debit"]
    for b in biaya:
        b["saldo"] = b["debit"] - b["kredit"]
    total_pendapatan = sum((p["saldo"] for p in pendapatan), Decimal("0"))
    total_biaya = sum((b["saldo"] for b in biaya), Decimal("0"))
    return {
        "pendapatan": pendapatan,
        "biaya": biaya,
        "total_pendapatan": total_pendapatan,
        "total_biaya": total_biaya,
        "laba_rugi": total_pendapatan - total_biaya,
    }


def neraca(db: Session, tahun_buku_id: int) -> dict:
    """Neraca/Balance Sheet. Laba/rugi periode berjalan (belum ditutup) ikut
    masuk sisi Modal supaya Aset = Liabilitas + Modal tetap balance, sesuai
    penyederhanaan MVP yang dipakai tutup_buku.py."""
    aset = _saldo_per_kategori(db, tahun_buku_id, KATEGORI_ASET)
    liabilitas = _saldo_per_kategori(db, tahun_buku_id, (KategoriAkun.UTANG,))
    modal = _saldo_per_kategori(db, tahun_buku_id, (KategoriAkun.MODAL,))
    for a in aset:
        a["saldo"] = a["debit"] - a["kredit"]
    for l in liabilitas:
        l["saldo"] = l["kredit"] - l["debit"]
    for m in modal:
        m["saldo"] = m["kredit"] - m["debit"]

    laba_rugi_periode = rugi_laba(db, tahun_buku_id)["laba_rugi"]

    total_aset = sum((a["saldo"] for a in aset), Decimal("0"))
    total_liabilitas = sum((l["saldo"] for l in liabilitas), Decimal("0"))
    total_modal = sum((m["saldo"] for m in modal), Decimal("0")) + laba_rugi_periode

    return {
        "aset": aset, "liabilitas": liabilitas, "modal": modal,
        "laba_rugi_periode": laba_rugi_periode,
        "total_aset": total_aset,
        "total_liabilitas": total_liabilitas,
        "total_modal": total_modal,
        "balance": total_aset == total_liabilitas + total_modal,
    }


def perubahan_modal(db: Session, tahun_buku_id: int) -> dict:
    modal = _saldo_per_kategori(db, tahun_buku_id, (KategoriAkun.MODAL,))
    modal_awal = sum((m["kredit"] - m["debit"] for m in modal), Decimal("0"))
    laba_rugi_periode = rugi_laba(db, tahun_buku_id)["laba_rugi"]
    return {
        "modal_awal": modal_awal,
        "laba_rugi_periode": laba_rugi_periode,
        "modal_akhir": modal_awal + laba_rugi_periode,
    }


def arus_kas(db: Session, tahun_buku_id: int, akun_kas_ids: Optional[list[int]] = None) -> dict:
    """Arus kas disederhanakan (MVP): mutasi bersih akun-akun yang ditandai
    sebagai kas (akun_kas_ids -- diisi dari akun_kas_id yang dipakai modul
    Penerimaan/Pengeluaran). Kalau tidak diisi, heuristik nama akun ILIKE
    '%kas%' dipakai sebagai fallback."""
    query = db.query(Akun.id, Akun.kode, Akun.nama,
                      func.coalesce(func.sum(JurnalDetail.debit), 0),
                      func.coalesce(func.sum(JurnalDetail.kredit), 0))
    if akun_kas_ids:
        query = query.filter(Akun.id.in_(akun_kas_ids))
    else:
        query = query.filter(Akun.nama.ilike("%kas%")).filter(Akun.kategori == KategoriAkun.HARTA)
    rows = (
        query.join(JurnalDetail, JurnalDetail.akun_id == Akun.id)
        .join(JurnalHeader, JurnalHeader.id == JurnalDetail.jurnal_header_id)
        .filter(JurnalHeader.tahun_buku_id == tahun_buku_id)
        .filter(JurnalHeader.status == StatusJurnal.AKTIF)
        .group_by(Akun.id, Akun.kode, Akun.nama)
        .order_by(Akun.kode)
        .all()
    )
    akun_list = []
    for a_id, kode, nama, debit, kredit in rows:
        akun_list.append({
            "akun_id": a_id, "kode": kode, "nama": nama,
            "kas_masuk": debit, "kas_keluar": kredit, "mutasi_bersih": debit - kredit,
        })
    total = sum((a["mutasi_bersih"] for a in akun_list), Decimal("0"))
    return {"akun": akun_list, "total_mutasi_bersih": total}
