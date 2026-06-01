from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import InsightsResponse
from services.data_fetcher import DataFetchError, InvalidRequestError
from services.insights_generator import get_ticker_insights

router = APIRouter(prefix="/api", tags=["insights"])


@router.get("/insights/{ticker}", response_model=InsightsResponse)
def get_insights(ticker: str) -> InsightsResponse:
    try:
        payload = get_ticker_insights(ticker)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DataFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return InsightsResponse.model_validate(payload)
