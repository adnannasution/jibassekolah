"""Router modul Referensi: Departemen, Kode Rekening Perkiraan (Akun), Tahun Buku, Tutup Buku."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.ledger import JurnalTidakBalanceError, TahunBukuTutupError
from app.core.tutup_buku import tutup_tahun_buku
from app.database import get_db
from app.models.referensi import Akun, Departemen, TahunBuku
from app.schemas.referensi import (
    AkunCreate, AkunOut, DepartemenCreate, DepartemenOut,
    TahunBukuCreate, TahunBukuOut, TutupBukuRequest,
)

router = APIRouter(prefix="/api/referensi", tags=["Referensi"])


# ---------- Departemen ----------
@router.get("/departemen", response_model=list[DepartemenOut])
def list_departemen(db: Session = Depends(get_db)):
    return db.query(Departemen).order_by(Departemen.nama).all()


@router.post("/departemen", response_model=DepartemenOut)
def tambah_departemen(data: DepartemenCreate, db: Session = Depends(get_db)):
    if db.query(Departemen).filter(Departemen.kode == data.kode).first():
        raise HTTPException(400, "Kode departemen sudah dipakai")
    obj = Departemen(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ---------- Akun (Kode Rekening Perkiraan) ----------
@router.get("/akun", response_model=list[AkunOut])
def list_akun(kategori: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Akun)
    if kategori:
        q = q.filter(Akun.kategori == kategori)
    return q.order_by(Akun.kode).all()


@router.post("/akun", response_model=AkunOut)
def tambah_akun(data: AkunCreate, db: Session = Depends(get_db)):
    if db.query(Akun).filter(Akun.kode == data.kode).first():
        raise HTTPException(400, "Kode akun sudah dipakai")
    obj = Akun(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/akun/{akun_id}", response_model=AkunOut)
def ubah_akun(akun_id: int, data: AkunCreate, db: Session = Depends(get_db)):
    obj = db.query(Akun).filter(Akun.id == akun_id).first()
    if obj is None:
        raise HTTPException(404, "Akun tidak ditemukan")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


# ---------- Tahun Buku ----------
@router.get("/tahun-buku", response_model=list[TahunBukuOut])
def list_tahun_buku(departemen_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(TahunBuku)
    if departemen_id:
        q = q.filter(TahunBuku.departemen_id == departemen_id)
    return q.order_by(TahunBuku.tanggal_mulai.desc()).all()


@router.post("/tahun-buku", response_model=TahunBukuOut)
def tambah_tahun_buku(data: TahunBukuCreate, db: Session = Depends(get_db)):
    """Dipakai cuma untuk tahun buku PERTAMA suatu departemen.
    Tahun buku berikutnya wajib lewat endpoint /tutup-buku."""
    existing_aktif = (
        db.query(TahunBuku)
        .filter(TahunBuku.departemen_id == data.departemen_id, TahunBuku.status == "AKTIF")
        .first()
    )
    if existing_aktif:
        raise HTTPException(400, "Departemen ini sudah punya tahun buku aktif")
    obj = TahunBuku(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/tutup-buku")
def proses_tutup_buku(
    data: TutupBukuRequest,
    petugas_id: int,  # TODO: ganti ke current_user dari auth dependency
    db: Session = Depends(get_db),
):
    try:
        hasil = tutup_tahun_buku(db, data, petugas_id)
        db.commit()
    except (JurnalTidakBalanceError, TahunBukuTutupError, ValueError) as e:
        db.rollback()
        raise HTTPException(400, str(e))

    return {
        "tahun_buku_lama": hasil["tahun_lama"].tahun_buku,
        "tahun_buku_baru": hasil["tahun_baru"].tahun_buku,
        "tahun_buku_baru_id": hasil["tahun_baru"].id,
        "laba_rugi_tahun_lama": float(hasil["laba_rugi"]),
    }
