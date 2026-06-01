from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from config import DATA_PERIOD, DEFAULT_INTERVAL
from models import OHLCResponse
from services.data_fetcher import DataFetchError, InvalidRequestError, fetch_ohlc

router = APIRouter(prefix="/api", tags=["market-data"])


@router.get("/ohlc/{ticker}", response_model=OHLCResponse)
def get_ohlc(
    ticker: str,
    period: str = Query(default=DATA_PERIOD),
    interval: str = Query(default=DEFAULT_INTERVAL),
) -> OHLCResponse:
    try:
        payload = fetch_ohlc(ticker=ticker, period=period, interval=interval)
    except InvalidRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DataFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return OHLCResponse.model_validate(payload)
