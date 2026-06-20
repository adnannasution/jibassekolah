"""Entrypoint aplikasi JIBAS Keuangan (versi modern)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import referensi

app = FastAPI(title="JIBAS Keuangan", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: persempit ke domain frontend produksi
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(referensi.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve frontend SPA (file statis) -- dipasang terakhir supaya tidak menabrak /api/*
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
