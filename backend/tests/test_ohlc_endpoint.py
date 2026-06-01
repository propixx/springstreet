from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from routers import ohlc


client = TestClient(app)


def test_ohlc_endpoint_returns_fetcher_payload(monkeypatch) -> None:
    def fake_fetch_ohlc(ticker: str, period: str, interval: str) -> dict:
        assert ticker == "AAPL"
        assert period == "5y"
        assert interval == "1d"
        return {
            "ticker": "AAPL",
            "currency": "USD",
            "data": [
                {
                    "date": "2024-01-02",
                    "open": 100.0,
                    "high": 103.0,
                    "low": 99.0,
                    "close": 102.0,
                    "volume": 1_000_000,
                }
            ],
            "metadata": {
                "name": "Apple Inc.",
                "sector": "Technology",
                "market_cap": 3_000_000_000_000,
                "pe_ratio": 30.5,
                "dividend_yield": 0.005,
                "52w_high": 199.62,
                "52w_low": 124.17,
                "current_price": 102.0,
            },
        }

    monkeypatch.setattr(ohlc, "fetch_ohlc", fake_fetch_ohlc)

    response = client.get("/api/ohlc/AAPL")

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["data"][0]["close"] == 102.0
    assert body["metadata"]["52w_high"] == 199.62
