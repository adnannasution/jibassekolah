"""
Koneksi database PostgreSQL (Railway).
DATABASE_URL diambil dari environment variable, contoh:
postgresql://user:pass@host:port/dbname
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/jibas_keuangan")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency FastAPI: satu session per request, otomatis ditutup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
