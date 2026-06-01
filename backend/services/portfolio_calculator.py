from __future__ import annotations

from typing import Any

import pandas as pd

from config import BENCHMARK_TICKER, INITIAL_INVESTMENT, PORTFOLIO_WEIGHTS, RISK_FREE_RATE, TICKERS
from services.data_fetcher import DataFetchError, fetch_ohlc
from services.metrics_engine import (
    annualize_return,
    annualized_volatility,
    as_percent,
    beta,
    max_drawdown_info,
    ohlc_to_frame,
    round_optional,
    rounded_ratio,
)


def calculate_portfolio() -> dict[str, Any]:
    stock_data = {ticker: fetch_ohlc(ticker)["data"] for ticker in TICKERS}
    close_prices = aligned_close_prices(stock_data)
    asset_values = portfolio_asset_values(close_prices)
    portfolio_values = asset_values.sum(axis=1)
    returns = portfolio_values.pct_change().dropna()

    total_return = portfolio_values.iloc[-1] / INITIAL_INVESTMENT - 1
    annualized_return = annualize_return(total_return, len(returns))
    volatility = annualized_volatility(returns)
    max_drawdown, _, _ = max_drawdown_info(portfolio_values)

    return {
        "initial_investment": float(INITIAL_INVESTMENT),
        "current_value": round(float(portfolio_values.iloc[-1]), 2),
        "total_return_pct": as_percent(total_return),
        "annualized_return_pct": as_percent(annualized_return),
        "portfolio_sharpe": rounded_ratio(annualized_return - RISK_FREE_RATE, volatility),
        "portfolio_max_drawdown_pct": as_percent(max_drawdown),
        "portfolio_volatility_pct": as_percent(volatility),
        "portfolio_beta": round_optional(portfolio_beta(returns)),
        "holdings": holdings(asset_values, float(portfolio_values.iloc[-1])),
        "daily_values": daily_values(asset_values, portfolio_values),
        "monthly_returns": monthly_returns(portfolio_values),
    }


def aligned_close_prices(stock_data: dict[str, list[dict[str, Any]]]) -> pd.DataFrame:
    closes = {ticker: ohlc_to_frame(data)["close"] for ticker, data in stock_data.items()}
    frame = pd.concat(closes, axis=1, join="inner").dropna()
    if len(frame) < 2:
        raise DataFetchError("Not enough overlapping trading days for the portfolio.")
    return frame


def portfolio_asset_values(close_prices: pd.DataFrame) -> pd.DataFrame:
    values = pd.DataFrame(index=close_prices.index)
    for ticker in TICKERS:
        starting_value = INITIAL_INVESTMENT * PORTFOLIO_WEIGHTS[ticker]
        values[ticker] = close_prices[ticker] / close_prices[ticker].iloc[0] * starting_value
    return values


def holdings(asset_values: pd.DataFrame, current_portfolio_value: float) -> list[dict[str, Any]]:
    total_gain = current_portfolio_value - INITIAL_INVESTMENT
    rows = []
    for ticker in TICKERS:
        starting_value = INITIAL_INVESTMENT * PORTFOLIO_WEIGHTS[ticker]
        current_value = float(asset_values[ticker].iloc[-1])
        contribution = 0.0 if total_gain == 0 else (current_value - starting_value) / total_gain
        rows.append(
            {
                "ticker": ticker,
                "weight": PORTFOLIO_WEIGHTS[ticker],
                "current_weight": round(current_value / current_portfolio_value, 4),
                "investment": round(starting_value, 2),
                "current_value": round(current_value, 2),
                "return_pct": as_percent(current_value / starting_value - 1),
                "contribution_pct": as_percent(contribution),
            }
        )
    return rows


def daily_values(asset_values: pd.DataFrame, portfolio_values: pd.Series) -> list[dict[str, Any]]:
    rows = []
    for date, values in asset_values.iterrows():
        row: dict[str, Any] = {"date": date.date().isoformat(), "value": round(float(portfolio_values.loc[date]), 2)}
        for ticker in TICKERS:
            row[ticker] = round(float(values[ticker]), 2)
        rows.append(row)
    return rows


def monthly_returns(portfolio_values: pd.Series) -> list[dict[str, Any]]:
    returns = portfolio_values.resample("ME").last().pct_change().dropna()
    return [{"month": date.strftime("%Y-%m"), "return_pct": as_percent(float(value))} for date, value in returns.items()]


def portfolio_beta(portfolio_returns: pd.Series) -> float | None:
    try:
        benchmark_data = fetch_ohlc(BENCHMARK_TICKER, allow_benchmark=True)["data"]
    except DataFetchError:
        return None

    benchmark_returns = ohlc_to_frame(benchmark_data)["close"].pct_change().dropna()
    return beta(portfolio_returns, benchmark_returns)
