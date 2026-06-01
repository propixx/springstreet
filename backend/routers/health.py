from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter

from config import APP_NAME, APP_VERSION, TICKERS
from models import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=APP_NAME,
        version=APP_VERSION,
        supported_tickers=TICKERS,
        timestamp=datetime.now(UTC),
    )
