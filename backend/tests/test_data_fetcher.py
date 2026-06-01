from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from services import data_fetcher
from services.data_fetcher import DataFetchError, InvalidRequestError, fetch_ohlc


def _history_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "High": [103.0, 105.0],
            "Low": [99.0, 101.0],
            "Close": [102.0, 104.0],
            "Volume": [1_000_000, 1_100_000],
        },
        index=pd.date_range("2024-01-02", periods=2, freq="D", tz="UTC"),
    )


class FakeTicker:
    info = {
        "longName": "Apple Inc.",
        "sector": "Technology",
        "currency": "USD",
        "marketCap": 3_000_000_000_000,
        "trailingPE": 30.5,
        "dividendYield": 0.005,
    }

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

    def history(self, period: str, interval: str, auto_adjust: bool) -> pd.DataFrame:
        assert self.ticker == "AAPL"
        assert period == "5y"
        assert interval == "1d"
        assert auto_adjust is False
        return _history_frame()


class BrokenTicker:
    info = {}

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

    def history(self, period: str, interval: str, auto_adjust: bool) -> pd.DataFrame:
        raise RuntimeError("network unavailable")


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(data_fetcher, "CACHE_DIR", tmp_path)
    return tmp_path


def test_fetch_ohlc_normalizes_yfinance_history(monkeypatch) -> None:
    monkeypatch.setattr(data_fetcher.yf, "Ticker", FakeTicker)

    payload = fetch_ohlc("aapl")

    assert payload["ticker"] == "AAPL"
    assert payload["currency"] == "USD"
    assert payload["metadata"]["name"] == "Apple Inc."
    assert payload["data"] == [
        {
            "date": "2024-01-02",
            "open": 100.0,
            "high": 103.0,
            "low": 99.0,
            "close": 102.0,
            "volume": 1_000_000,
        },
        {
            "date": "2024-01-03",
            "open": 102.0,
            "high": 105.0,
            "low": 101.0,
            "close": 104.0,
            "volume": 1_100_000,
        },
    ]


def test_fetch_ohlc_uses_fresh_cache(monkeypatch) -> None:
    monkeypatch.setattr(data_fetcher.yf, "Ticker", FakeTicker)
    first_payload = fetch_ohlc("AAPL")

    monkeypatch.setattr(data_fetcher.yf, "Ticker", BrokenTicker)
    second_payload = fetch_ohlc("AAPL")

    assert second_payload == first_payload


def test_fetch_ohlc_falls_back_to_stale_cache(monkeypatch) -> None:
    stale_payload = {
        "ticker": "AAPL",
        "currency": "USD",
        "data": [{"date": "2024-01-02", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1}],
        "metadata": {},
        "fetched_at": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
    }
    data_fetcher._write_cache("AAPL", "5y", "1d", stale_payload)
    monkeypatch.setattr(data_fetcher.yf, "Ticker", BrokenTicker)

    assert fetch_ohlc("AAPL") == stale_payload


def test_fetch_ohlc_raises_without_network_or_cache(monkeypatch) -> None:
    monkeypatch.setattr(data_fetcher.yf, "Ticker", BrokenTicker)

    with pytest.raises(DataFetchError):
        fetch_ohlc("AAPL")


def test_fetch_ohlc_rejects_unsupported_tickers() -> None:
    with pytest.raises(InvalidRequestError):
        fetch_ohlc("TSLA")
