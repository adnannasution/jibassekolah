"""Router Dashboard ringkasan -- satu endpoint agregat untuk landing page."""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import dashboard as dashboard_core
from app.database import get_db
from app.schemas.dashboard import DashboardRingkasanOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/ringkasan", response_model=DashboardRingkasanOut)
def get_ringkasan_dashboard(
    tahun_buku_id: int, departemen_id: Optional[int] = None, db: Session = Depends(get_db)
):
    return dashboard_core.ringkasan_dashboard(db, tahun_buku_id, departemen_id)
