from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from config import BENCHMARK_TICKER, RISK_FREE_RATE, TRADING_DAYS_PER_YEAR
from services.data_fetcher import DataFetchError, fetch_ohlc


def get_ticker_metrics(ticker: str) -> dict[str, Any]:
    stock = fetch_ohlc(ticker)
    benchmark = _fetch_benchmark()
    benchmark_data = benchmark["data"] if benchmark else None
    return {"ticker": stock["ticker"], "metrics": calculate_ticker_metrics(stock["data"], benchmark_data)}


def calculate_ticker_metrics(
    data: list[dict[str, Any]],
    benchmark_data: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    frame = ohlc_to_frame(data)
    benchmark_frame = ohlc_to_frame(benchmark_data) if benchmark_data else None
    return calculate_metrics_from_frame(frame, benchmark_frame)


def calculate_metrics_from_frame(frame: pd.DataFrame, benchmark_frame: pd.DataFrame | None = None) -> dict[str, Any]:
    if len(frame) < 2:
        raise DataFetchError("At least two price rows are required.")

    close = frame["close"]
    returns = close.pct_change().dropna()
    total_return = close.iloc[-1] / close.iloc[0] - 1
    annualized_return = annualize_return(total_return, len(returns))
    volatility = annualized_volatility(returns)
    downside_volatility = annualized_volatility(returns[returns < 0])
    max_drawdown, drawdown_start, drawdown_end = max_drawdown_info(close)
    benchmark_returns = benchmark_frame["close"].pct_change().dropna() if benchmark_frame is not None else None

    return {
        "total_return_pct": as_percent(total_return),
        "annualized_return_pct": as_percent(annualized_return),
        "volatility_pct": as_percent(volatility),
        "sharpe_ratio": rounded_ratio(annualized_return - RISK_FREE_RATE, volatility),
        "sortino_ratio": rounded_ratio(annualized_return - RISK_FREE_RATE, downside_volatility),
        "max_drawdown_pct": as_percent(max_drawdown),
        "max_drawdown_start": date_string(drawdown_start),
        "max_drawdown_end": date_string(drawdown_end),
        "beta": round_optional(beta(returns, benchmark_returns)),
        "avg_daily_volume": round(float(frame["volume"].mean()), 2),
        "best_day": day_return(returns.idxmax(), returns.max()) if not returns.empty else None,
        "worst_day": day_return(returns.idxmin(), returns.min()) if not returns.empty else None,
        "positive_days_pct": as_percent(float((returns > 0).mean())) if not returns.empty else 0.0,
        "current_streak": current_streak(returns),
    }


def ohlc_to_frame(data: list[dict[str, Any]] | None) -> pd.DataFrame:
    if not data:
        raise DataFetchError("OHLC data is empty.")

    frame = pd.DataFrame(data)
    required = {"date", "open", "high", "low", "close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise DataFetchError(f"OHLC data is missing fields: {', '.join(sorted(missing))}.")

    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values("date").set_index("date")
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["open", "high", "low", "close"])
    if len(frame) < 2:
        raise DataFetchError("OHLC data has too few valid rows.")
    return frame


def annualize_return(total_return: float, return_count: int) -> float:
    if return_count <= 0 or total_return <= -1:
        return 0.0
    years = return_count / TRADING_DAYS_PER_YEAR
    return (1 + total_return) ** (1 / years) - 1


def annualized_volatility(returns: pd.Series) -> float:
    # Volatility is the standard deviation of daily returns scaled to a trading year.
    if returns.empty:
        return 0.0
    return float(returns.std(ddof=0) * math.sqrt(TRADING_DAYS_PER_YEAR))


def max_drawdown_info(prices: pd.Series) -> tuple[float, pd.Timestamp, pd.Timestamp]:
    # Drawdown compares the portfolio/stock value to its previous running peak.
    cumulative = prices / prices.iloc[0]
    running_peak = cumulative.cummax()
    drawdowns = cumulative / running_peak - 1
    end = drawdowns.idxmin()
    start = cumulative.loc[:end].idxmax()
    return float(drawdowns.loc[end]), start, end


def beta(stock_returns: pd.Series, benchmark_returns: pd.Series | None) -> float | None:
    if benchmark_returns is None:
        return None
    aligned = pd.concat([stock_returns, benchmark_returns], axis=1, join="inner").dropna()
    aligned.columns = ["stock", "benchmark"]
    if len(aligned) < 2:
        return None
    benchmark_variance = float(aligned["benchmark"].var(ddof=0))
    if math.isclose(benchmark_variance, 0.0):
        return None
    covariance = float(np.cov(aligned["stock"], aligned["benchmark"], ddof=0)[0][1])
    return covariance / benchmark_variance


def current_streak(returns: pd.Series) -> dict[str, Any]:
    if returns.empty:
        return {"direction": "flat", "days": 0}

    latest_direction = direction_for_return(float(returns.iloc[-1]))
    days = 0
    for value in reversed(returns.tolist()):
        if direction_for_return(float(value)) != latest_direction:
            break
        days += 1
    return {"direction": latest_direction, "days": days}


def direction_for_return(value: float) -> str:
    if value > 0:
        return "up"
    if value < 0:
        return "down"
    return "flat"


def day_return(date: pd.Timestamp, value: float) -> dict[str, Any]:
    return {"date": date.date().isoformat(), "return_pct": as_percent(float(value))}


def as_percent(value: float) -> float:
    return round(float(value) * 100, 2)


def rounded_ratio(numerator: float, denominator: float) -> float | None:
    if math.isclose(denominator, 0.0):
        return None
    return round(numerator / denominator, 2)


def round_optional(value: float | None) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(float(value), 2)


def date_string(value: pd.Timestamp) -> str:
    return value.date().isoformat()


def _fetch_benchmark() -> dict[str, Any] | None:
    try:
        return fetch_ohlc(BENCHMARK_TICKER, allow_benchmark=True)
    except DataFetchError:
        return None
