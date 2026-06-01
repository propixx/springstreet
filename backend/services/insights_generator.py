from __future__ import annotations

import math
from typing import Any

from services.data_fetcher import fetch_ohlc
from services.metrics_engine import calculate_ticker_metrics, ohlc_to_frame


def get_ticker_insights(ticker: str) -> dict[str, Any]:
    payload = fetch_ohlc(ticker)
    frame = ohlc_to_frame(payload["data"])
    metrics = calculate_ticker_metrics(payload["data"])

    insights = [
        trend_insight(payload["ticker"], frame),
        volatility_insight(payload["ticker"], frame),
        drawdown_insight(payload["ticker"], metrics),
        momentum_insight(payload["ticker"], frame),
    ]

    volume = volume_insight(payload["ticker"], frame)
    if volume:
        insights.append(volume)

    return {"ticker": payload["ticker"], "insights": insights}


def trend_insight(ticker: str, frame) -> dict[str, Any]:
    close = frame["close"]
    window = 200 if len(close) >= 200 else min(50, len(close))
    moving_average = close.rolling(window).mean().iloc[-1]
    distance = (close.iloc[-1] / moving_average - 1) * 100

    if distance >= 10:
        severity, title = "positive", "Strong Uptrend"
    elif distance >= 0:
        severity, title = "positive", "Above Moving Average"
    elif distance <= -10:
        severity, title = "negative", "Strong Downtrend"
    else:
        severity, title = "warning", "Below Moving Average"

    return {
        "type": "trend",
        "severity": severity,
        "title": title,
        "description": f"{ticker} is trading {abs(distance):.1f}% {'above' if distance >= 0 else 'below'} its {window}-day moving average.",
        "metric_value": round(float(distance), 2),
    }


def volatility_insight(ticker: str, frame) -> dict[str, Any]:
    returns = frame["close"].pct_change().dropna()
    rolling_vol = returns.rolling(30).std(ddof=0) * math.sqrt(252) * 100
    usable = rolling_vol.dropna()
    current_vol = float(usable.iloc[-1]) if not usable.empty else 0.0
    average_vol = float(usable.tail(252).mean()) if not usable.empty else current_vol

    if average_vol and current_vol > average_vol * 1.2:
        severity, title = "warning", "Elevated Volatility"
    elif average_vol and current_vol < average_vol * 0.8:
        severity, title = "info", "Subdued Volatility"
    else:
        severity, title = "info", "Normal Volatility"

    return {
        "type": "volatility",
        "severity": severity,
        "title": title,
        "description": f"{ticker}'s 30-day volatility is {current_vol:.1f}% versus a recent average of {average_vol:.1f}%.",
        "metric_value": round(current_vol, 2),
    }


def drawdown_insight(ticker: str, metrics: dict[str, Any]) -> dict[str, Any]:
    drawdown = metrics["max_drawdown_pct"]
    return {
        "type": "drawdown",
        "severity": "warning" if drawdown <= -25 else "info",
        "title": "Drawdown Profile",
        "description": f"{ticker}'s worst drawdown in the selected period was {drawdown:.1f}%.",
        "metric_value": drawdown,
    }


def momentum_insight(ticker: str, frame) -> dict[str, Any]:
    close = frame["close"]
    lookback = min(14, len(close) - 1)
    momentum = (close.iloc[-1] / close.iloc[-1 - lookback] - 1) * 100 if lookback > 0 else 0.0

    if momentum >= 5:
        severity, title = "positive", "Positive Momentum"
    elif momentum <= -5:
        severity, title = "warning", "Weak Momentum"
    else:
        severity, title = "info", "Neutral Momentum"

    return {
        "type": "momentum",
        "severity": severity,
        "title": title,
        "description": f"{ticker}'s trailing {lookback}-session move is {momentum:.1f}%.",
        "metric_value": round(float(momentum), 2),
    }


def volume_insight(ticker: str, frame) -> dict[str, Any] | None:
    if len(frame) < 20:
        return None
    recent = float(frame["volume"].tail(5).mean())
    baseline = float(frame["volume"].tail(20).mean())
    if baseline == 0:
        return None

    difference = (recent / baseline - 1) * 100
    if difference >= 30:
        severity, title = "warning", "Unusual Volume"
    elif difference <= -30:
        severity, title = "info", "Low Activity"
    else:
        severity, title = "info", "Normal Volume"

    return {
        "type": "volume",
        "severity": severity,
        "title": title,
        "description": f"{ticker}'s recent volume is {abs(difference):.1f}% {'above' if difference >= 0 else 'below'} its 20-session average.",
        "metric_value": round(float(difference), 2),
    }
