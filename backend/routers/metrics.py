from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import MetricsResponse
from services.data_fetcher import DataFetchError, InvalidRequestError
from services.metrics_engine import get_ticker_metrics

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/metrics/{ticker}", response_model=MetricsResponse)
def get_metrics(ticker: str) -> MetricsResponse:
    try:
        payload = get_ticker_metrics(ticker)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DataFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return MetricsResponse.model_validate(payload)
