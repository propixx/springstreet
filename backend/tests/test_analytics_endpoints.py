from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from routers import insights, metrics, portfolio


client = TestClient(app)


def sample_metrics_payload() -> dict:
    return {
        "ticker": "AAPL",
        "metrics": {
            "total_return_pct": 20.0,
            "annualized_return_pct": 10.0,
            "volatility_pct": 18.0,
            "sharpe_ratio": 0.75,
            "sortino_ratio": 1.1,
            "max_drawdown_pct": -8.0,
            "max_drawdown_start": "2024-01-03",
            "max_drawdown_end": "2024-01-10",
            "beta": 1.05,
            "avg_daily_volume": 1_000_000.0,
            "best_day": {"date": "2024-01-05", "return_pct": 3.0},
            "worst_day": {"date": "2024-01-09", "return_pct": -2.5},
            "positive_days_pct": 55.0,
            "current_streak": {"direction": "up", "days": 2},
        },
    }


def sample_portfolio_payload() -> dict:
    return {
        "initial_investment": 10_000.0,
        "current_value": 12_000.0,
        "total_return_pct": 20.0,
        "annualized_return_pct": 10.0,
        "portfolio_sharpe": 0.8,
        "portfolio_max_drawdown_pct": -6.0,
        "portfolio_volatility_pct": 15.0,
        "portfolio_beta": 1.0,
        "holdings": [
            {
                "ticker": "AAPL",
                "weight": 0.2,
                "current_weight": 0.25,
                "investment": 2_000.0,
                "current_value": 3_000.0,
                "return_pct": 50.0,
                "contribution_pct": 50.0,
            }
        ],
        "daily_values": [{"date": "2024-01-02", "value": 10_000.0, "AAPL": 2_000.0}],
        "monthly_returns": [{"month": "2024-02", "return_pct": 2.0}],
    }


def sample_insights_payload() -> dict:
    return {
        "ticker": "AAPL",
        "insights": [
            {
                "type": "trend",
                "severity": "positive",
                "title": "Above Moving Average",
                "description": "AAPL is trading above its moving average.",
                "metric_value": 5.0,
            }
        ],
    }


def test_metrics_endpoint_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "get_ticker_metrics", lambda ticker: sample_metrics_payload())

    response = client.get("/api/metrics/AAPL")

    assert response.status_code == 200
    assert response.json()["metrics"]["total_return_pct"] == 20.0


def test_portfolio_endpoint_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(portfolio, "calculate_portfolio", sample_portfolio_payload)

    response = client.get("/api/portfolio")

    assert response.status_code == 200
    assert response.json()["current_value"] == 12_000.0


def test_insights_endpoint_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(insights, "get_ticker_insights", lambda ticker: sample_insights_payload())

    response = client.get("/api/insights/AAPL")

    assert response.status_code == 200
    assert response.json()["insights"][0]["type"] == "trend"
