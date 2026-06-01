from __future__ import annotations

from fastapi.testclient import TestClient

from config import APP_NAME, APP_VERSION, TICKERS
from main import app


client = TestClient(app)


def test_health_endpoint_returns_backend_status() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == APP_NAME
    assert body["version"] == APP_VERSION
    assert body["supported_tickers"] == TICKERS
    assert "timestamp" in body


def test_cors_allows_local_next_development_origin() -> None:
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
