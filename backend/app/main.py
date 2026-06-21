"""Entrypoint aplikasi JIBAS Keuangan (versi modern)."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.seed import seed_admin_pertama
from app.database import SessionLocal
from app.routers import inventory, jurnal_umum, laporan, pengaturan, pengeluaran, penerimaan, referensi, siswa

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(title="Brilliant Finance", version="0.1.0")


@app.on_event("startup")
def _seed_admin_pertama():
    db = SessionLocal()
    try:
        seed_admin_pertama(db)
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: persempit ke domain frontend produksi
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(referensi.router)
app.include_router(siswa.router)
app.include_router(penerimaan.router)
app.include_router(pengeluaran.router)
app.include_router(jurnal_umum.router)
app.include_router(laporan.router)
app.include_router(inventory.router)
app.include_router(pengaturan.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve frontend SPA (file statis) -- dipasang terakhir supaya tidak menabrak /api/*
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
