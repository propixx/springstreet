from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    supported_tickers: list[str]
    timestamp: datetime


class ErrorResponse(BaseModel):
    detail: str
    code: str


class OHLCDatum(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class TickerMetadata(BaseModel):
    name: str | None = None
    sector: str | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    fifty_two_week_high: float | None = Field(default=None, alias="52w_high")
    fifty_two_week_low: float | None = Field(default=None, alias="52w_low")
    current_price: float | None = None


class OHLCResponse(BaseModel):
    ticker: str
    currency: str
    data: list[OHLCDatum]
    metadata: TickerMetadata


class DayReturn(BaseModel):
    date: str
    return_pct: float


class Streak(BaseModel):
    direction: str
    days: int


class TickerMetrics(BaseModel):
    total_return_pct: float
    annualized_return_pct: float
    volatility_pct: float
    sharpe_ratio: float | None
    sortino_ratio: float | None
    max_drawdown_pct: float
    max_drawdown_start: str | None
    max_drawdown_end: str | None
    beta: float | None
    avg_daily_volume: float
    best_day: DayReturn | None
    worst_day: DayReturn | None
    positive_days_pct: float
    current_streak: Streak


class MetricsResponse(BaseModel):
    ticker: str
    metrics: TickerMetrics


class PortfolioHolding(BaseModel):
    ticker: str
    weight: float
    current_weight: float
    investment: float
    current_value: float
    return_pct: float
    contribution_pct: float


class MonthlyReturn(BaseModel):
    month: str
    return_pct: float


class PortfolioResponse(BaseModel):
    initial_investment: float
    current_value: float
    total_return_pct: float
    annualized_return_pct: float
    portfolio_sharpe: float | None
    portfolio_max_drawdown_pct: float
    portfolio_volatility_pct: float
    portfolio_beta: float | None
    holdings: list[PortfolioHolding]
    daily_values: list[dict[str, Any]]
    monthly_returns: list[MonthlyReturn]


class Insight(BaseModel):
    type: str
    severity: str
    title: str
    description: str
    metric_value: float | None = None


class InsightsResponse(BaseModel):
    ticker: str
    insights: list[Insight]
