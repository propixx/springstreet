from __future__ import annotations

import json
import math
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from config import (
    BENCHMARK_TICKER,
    CACHE_TTL_HOURS,
    DATA_PERIOD,
    DEFAULT_INTERVAL,
    TICKERS,
    VALID_INTERVALS,
    VALID_PERIODS,
)

CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"


class InvalidRequestError(ValueError):
    pass


class DataFetchError(RuntimeError):
    pass


def fetch_ohlc(
    ticker: str,
    period: str = DATA_PERIOD,
    interval: str = DEFAULT_INTERVAL,
    allow_benchmark: bool = False,
) -> dict[str, Any]:
    normalized_ticker = _validate_ticker(ticker, allow_benchmark=allow_benchmark)
    _validate_period(period)
    _validate_interval(interval)

    cached_payload = _read_cache(normalized_ticker, period, interval)
    if cached_payload and not _is_stale(cached_payload):
        return cached_payload

    try:
        payload = _fetch_from_yfinance(normalized_ticker, period, interval)
    except Exception as exc:
        if cached_payload:
            return cached_payload
        raise DataFetchError(f"Unable to fetch OHLC data for {normalized_ticker}.") from exc

    _write_cache(normalized_ticker, period, interval, payload)
    return payload


def _fetch_from_yfinance(ticker: str, period: str, interval: str) -> dict[str, Any]:
    ticker_obj = yf.Ticker(ticker)
    frame = ticker_obj.history(period=period, interval=interval, auto_adjust=False)
    data = _normalize_history(frame)
    if not data:
        raise DataFetchError(f"No OHLC rows returned for {ticker}.")

    metadata, currency = _build_metadata(ticker_obj, frame, data)
    return {
        "ticker": ticker,
        "currency": currency,
        "data": data,
        "metadata": metadata,
        "fetched_at": datetime.now(UTC).isoformat(),
    }


def _normalize_history(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []

    columns = {str(column).lower(): column for column in frame.columns}
    required = ["open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in columns]
    if missing:
        raise DataFetchError(f"OHLC data is missing required columns: {', '.join(missing)}.")

    normalized = frame[[columns[column] for column in required]].copy()
    normalized.columns = required
    normalized = normalized.dropna(subset=["open", "high", "low", "close"])

    rows: list[dict[str, Any]] = []
    for index, row in normalized.iterrows():
        rows.append(
            {
                "date": pd.to_datetime(index).date().isoformat(),
                "open": _clean_float(row["open"]),
                "high": _clean_float(row["high"]),
                "low": _clean_float(row["low"]),
                "close": _clean_float(row["close"]),
                "volume": int(0 if pd.isna(row["volume"]) else row["volume"]),
            }
        )
    return rows


def _build_metadata(ticker_obj: Any, frame: pd.DataFrame, data: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    info = _safe_info(ticker_obj)
    latest = data[-1]
    recent_frame = frame.tail(252)

    current_price = _first_present(info, "currentPrice", "regularMarketPrice", "previousClose")
    if current_price is None:
        current_price = latest["close"]

    metadata = {
        "name": _first_present(info, "longName", "shortName"),
        "sector": _first_present(info, "sector"),
        "market_cap": _clean_optional_float(_first_present(info, "marketCap")),
        "pe_ratio": _clean_optional_float(_first_present(info, "trailingPE", "forwardPE")),
        "dividend_yield": _clean_optional_float(_first_present(info, "dividendYield")),
        "52w_high": _clean_optional_float(_first_present(info, "fiftyTwoWeekHigh")) or _series_max(recent_frame, "High"),
        "52w_low": _clean_optional_float(_first_present(info, "fiftyTwoWeekLow")) or _series_min(recent_frame, "Low"),
        "current_price": _clean_optional_float(current_price),
    }
    currency = str(_first_present(info, "currency") or "USD")
    return metadata, currency


def _safe_info(ticker_obj: Any) -> dict[str, Any]:
    try:
        info = getattr(ticker_obj, "info", {})
    except Exception:
        return {}
    return info if isinstance(info, dict) else {}


def _read_cache(ticker: str, period: str, interval: str) -> dict[str, Any] | None:
    path = _cache_path(ticker, period, interval)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_cache(ticker: str, period: str, interval: str, payload: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(ticker, period, interval)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def _is_stale(payload: dict[str, Any]) -> bool:
    fetched_at = payload.get("fetched_at")
    if not isinstance(fetched_at, str):
        return True
    try:
        fetched_time = datetime.fromisoformat(fetched_at)
    except ValueError:
        return True
    if fetched_time.tzinfo is None:
        fetched_time = fetched_time.replace(tzinfo=UTC)
    return datetime.now(UTC) - fetched_time > timedelta(hours=CACHE_TTL_HOURS)


def _cache_path(ticker: str, period: str, interval: str) -> Path:
    cache_key = "_".join([_safe_token(ticker), _safe_token(period), _safe_token(interval)])
    return CACHE_DIR / f"{cache_key}.json"


def _safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]", "", value)
    if not token:
        raise InvalidRequestError("Cache key contains no valid characters.")
    return token


def _validate_ticker(ticker: str, allow_benchmark: bool = False) -> str:
    normalized = ticker.strip().upper()
    allowed = [*TICKERS, BENCHMARK_TICKER] if allow_benchmark else TICKERS
    if normalized not in allowed:
        supported = ", ".join(TICKERS)
        raise InvalidRequestError(f"Unsupported ticker '{ticker}'. Supported tickers: {supported}.")
    return normalized


def _validate_period(period: str) -> None:
    if period not in VALID_PERIODS:
        supported = ", ".join(sorted(VALID_PERIODS))
        raise InvalidRequestError(f"Unsupported period '{period}'. Supported periods: {supported}.")


def _validate_interval(interval: str) -> None:
    if interval not in VALID_INTERVALS:
        supported = ", ".join(sorted(VALID_INTERVALS))
        raise InvalidRequestError(f"Unsupported interval '{interval}'. Supported intervals: {supported}.")


def _first_present(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return None


def _series_max(frame: pd.DataFrame, column: str) -> float | None:
    if column not in frame or frame[column].empty:
        return None
    return _clean_optional_float(frame[column].max())


def _series_min(frame: pd.DataFrame, column: str) -> float | None:
    if column not in frame or frame[column].empty:
        return None
    return _clean_optional_float(frame[column].min())


def _clean_float(value: Any) -> float:
    cleaned = _clean_optional_float(value)
    if cleaned is None:
        raise DataFetchError("OHLC data contains a non-numeric required value.")
    return cleaned


def _clean_optional_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return round(number, 4)
