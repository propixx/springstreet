from __future__ import annotations

APP_NAME = "Spring Street Market Insights API"
APP_VERSION = "0.1.0"

TICKERS = ["AAPL", "MSFT", "AMZN", "JPM", "JNJ"]
BENCHMARK_TICKER = "SPY"
PORTFOLIO_WEIGHTS = {ticker: 0.20 for ticker in TICKERS}
INITIAL_INVESTMENT = 10_000
DATA_PERIOD = "5y"
CACHE_TTL_HOURS = 1
DEFAULT_INTERVAL = "1d"
VALID_PERIODS = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"}
VALID_INTERVALS = {"1d", "1wk", "1mo"}
RISK_FREE_RATE = 0.045
TRADING_DAYS_PER_YEAR = 252

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://springstreet-dashboard.onrender.com",
]
