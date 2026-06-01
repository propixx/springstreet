from __future__ import annotations

from datetime import date, timedelta

import pytest

from config import INITIAL_INVESTMENT, TICKERS
from services import insights_generator, portfolio_calculator
from services.metrics_engine import calculate_ticker_metrics
from services.portfolio_calculator import calculate_portfolio


def make_ohlc(closes: list[float], start: date = date(2024, 1, 2)) -> list[dict]:
    rows = []
    for index, close in enumerate(closes):
        rows.append(
            {
                "date": (start + timedelta(days=index)).isoformat(),
                "open": close,
                "high": close * 1.02,
                "low": close * 0.98,
                "close": close,
                "volume": 1_000_000 + index,
            }
        )
    return rows


def test_calculate_ticker_metrics_uses_expected_return_and_drawdown_math() -> None:
    stock = make_ohlc([100, 110, 105, 120])
    benchmark = make_ohlc([100, 102, 101, 106])

    metrics = calculate_ticker_metrics(stock, benchmark)

    assert metrics["total_return_pct"] == 20.0
    assert metrics["max_drawdown_pct"] == -4.55
    assert metrics["best_day"]["return_pct"] == 14.29
    assert metrics["worst_day"]["return_pct"] == -4.55
    assert metrics["current_streak"] == {"direction": "up", "days": 1}
    assert metrics["beta"] is not None


def test_calculate_portfolio_normalizes_equal_weight_holdings(monkeypatch) -> None:
    flat = make_ohlc([100, 100, 100])
    doubled = make_ohlc([100, 150, 200])
    benchmark = make_ohlc([100, 105, 110])

    def fake_fetch_ohlc(ticker: str, *args, **kwargs) -> dict:
        data = benchmark if kwargs.get("allow_benchmark") else doubled if ticker == "AAPL" else flat
        return {"ticker": ticker, "currency": "USD", "data": data, "metadata": {}}

    monkeypatch.setattr(portfolio_calculator, "fetch_ohlc", fake_fetch_ohlc)

    portfolio = calculate_portfolio()

    assert portfolio["initial_investment"] == float(INITIAL_INVESTMENT)
    assert portfolio["current_value"] == 12_000.0
    assert portfolio["total_return_pct"] == 20.0
    assert len(portfolio["holdings"]) == len(TICKERS)
    assert portfolio["holdings"][0]["ticker"] == "AAPL"
    assert portfolio["holdings"][0]["current_value"] == 4_000.0
    assert portfolio["holdings"][0]["current_weight"] == pytest.approx(0.3333)
    assert portfolio["daily_values"][-1]["value"] == 12_000.0


def test_get_ticker_insights_returns_clear_rule_based_cards(monkeypatch) -> None:
    rising_prices = [100 + index for index in range(60)]

    def fake_fetch_ohlc(ticker: str, *args, **kwargs) -> dict:
        return {"ticker": ticker.upper(), "currency": "USD", "data": make_ohlc(rising_prices), "metadata": {}}

    monkeypatch.setattr(insights_generator, "fetch_ohlc", fake_fetch_ohlc)

    payload = insights_generator.get_ticker_insights("aapl")

    insight_types = {insight["type"] for insight in payload["insights"]}
    assert payload["ticker"] == "AAPL"
    assert {"trend", "volatility", "drawdown", "momentum", "volume"}.issubset(insight_types)
