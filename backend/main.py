from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_NAME, APP_VERSION, CORS_ORIGINS
from routers import health, insights, metrics, ohlc, portfolio


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="Market data and portfolio analytics API for the Spring Street dashboard.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(ohlc.router)
    app.include_router(metrics.router)
    app.include_router(portfolio.router)
    app.include_router(insights.router)
    return app


app = create_app()
