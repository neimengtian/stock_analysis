import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_stock():
    response = client.post("/stocks/", json={"ticker": "AAPL", "name": "Apple Inc."})
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"


def test_get_stock():
    client.post("/stocks/", json={"ticker": "AAPL"})
    response = client.get("/stocks/AAPL")
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"


def test_get_stock_not_found():
    response = client.get("/stocks/INVALID")
    assert response.status_code == 404
