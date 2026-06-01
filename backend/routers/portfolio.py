from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import PortfolioResponse
from services.data_fetcher import DataFetchError
from services.portfolio_calculator import calculate_portfolio

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio() -> PortfolioResponse:
    try:
        payload = calculate_portfolio()
    except DataFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return PortfolioResponse.model_validate(payload)
