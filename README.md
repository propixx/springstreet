# Market Insights Dashboard

Hi, I am Pratyush Biswal from IIT Kanpur. I built this project for the Spring Street internship assignment as a small full-stack dashboard for exploring market data, portfolio movement, and basic risk-return metrics.

The project is not meant to be a trading tool. It is an explainable finance dashboard where the data flow, formulas, and UI choices are simple enough to discuss in an interview.

## What This Project Is

This is a FastAPI + Next.js dashboard that pulls daily OHLC market data for five stocks, builds a simple equal-weighted portfolio, and shows the results through charts, KPI cards, and rule-based notes.

Supported tickers:

- `AAPL`
- `MSFT`
- `AMZN`
- `JPM`
- `JNJ`

## Why I Built It

I wanted the assignment to show that I can connect a real data source to a clean frontend while keeping the calculations understandable. I used an equal-weighted portfolio of five stocks to keep the analysis simple and explainable.

I also kept the insights rule-based so the logic remains easy to verify. Each note comes from a metric such as trend, volatility, drawdown, momentum, or volume.

## Tech Stack

- Backend: FastAPI, pandas, numpy, yfinance, Pydantic, pytest
- Frontend: Next.js 15, TypeScript, React
- Charts: TradingView Lightweight Charts for OHLC candles, Recharts for portfolio charts
- Data: Yahoo Finance through `yfinance`

## Features

- Fetches 5 years of daily OHLC data from Yahoo Finance.
- Caches successful market-data responses for one hour in `backend/cache/`.
- Falls back to the last good cached response if a live fetch fails.
- Shows a candlestick chart with volume for the selected ticker.
- Calculates return, annualized return, volatility, Sharpe ratio, max drawdown, beta, and other basic metrics.
- Builds a hypothetical `$10,000` equal-weight portfolio with 20% in each ticker.
- Shows portfolio value, current allocation, holding returns, and allocation drift.
- Displays rule-based notes for ticker behavior and portfolio performance.
- Handles loading, empty, and backend-offline states with retry buttons.

## Assumptions

- The portfolio starts at `$10,000`.
- Each supported ticker starts at a fixed 20% portfolio weight.
- Daily market data comes from Yahoo Finance, so live requests depend on network availability.
- Beta calculations use `SPY` internally as the benchmark.
- The risk-free rate is set to 4.5% for Sharpe and Sortino calculations.
- This is an educational dashboard, not investment advice.

## How To Run It

Run the backend:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Run the frontend in a second terminal:

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Open:

```text
http://127.0.0.1:3000
```

The frontend expects the backend at `http://localhost:8000`. If you run the backend somewhere else, create `frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For deployment, set `NEXT_PUBLIC_API_URL` to the deployed FastAPI backend URL before building the frontend.

## Backend API Routes

Base URL:

```text
http://localhost:8000
```

Routes:

- `GET /api/health`
- `GET /api/ohlc/{ticker}`
- `GET /api/metrics/{ticker}`
- `GET /api/portfolio`
- `GET /api/insights/{ticker}`

FastAPI docs are available at:

```text
http://localhost:8000/docs
```

## Deployment Notes

The app is ready to deploy as two services:

- Frontend: configured for Render at `https://springstreet-dashboard.onrender.com`.
- Backend: deployed on Render at `https://springstreet-api.onrender.com`.

Required frontend environment variable: `NEXT_PUBLIC_API_URL`, set to the full URL of the deployed FastAPI backend.

The backend uses Render's free plan, so the first request may take a few seconds because of cold start. Live market data can also be affected by Yahoo Finance or `yfinance` availability.

## Checks

Backend:

```bash
cd backend
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm.cmd run lint
npm.cmd run build
```

## Notes On The Calculations

- Total return is `(ending price / starting price) - 1`.
- Annualized return scales the total return over the number of trading days.
- Volatility is the standard deviation of daily returns scaled by `sqrt(252)`.
- Sharpe ratio uses the annualized return, volatility, and a 4.5% risk-free rate.
- Max drawdown compares each value against its previous running peak.
- Portfolio values normalize each holding to its starting allocation, then sum the daily values.

I kept these formulas in plain pandas/numpy code so they are easy to audit.

## Known Limitations

- The dashboard currently uses a fixed 5-year daily data period.
- The portfolio is intentionally simple: five stocks, equal starting weights, and no deposits or rebalancing.
- Live data depends on Yahoo Finance through `yfinance`.
- The frontend needs a reachable backend URL for the charts and metrics to load after deployment.

## Things I Would Improve With More Time

- Add a clearer benchmark comparison view against `SPY`.
- Add date-range controls instead of always showing the default 5-year period.
- Add better deployment monitoring and error reporting for hosted services.
- Add more tests around edge cases like missing market-data columns or short ticker histories.
- Add a small screenshot section after deployment so the README is easier to scan.
