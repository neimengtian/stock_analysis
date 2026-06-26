import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.storage.database import Base
from src.storage.models import Stock, StockPrice, MLPrediction
from src.storage.crud import create_stock, get_stock, store_prices, store_prediction
from src.data.models import OHLCV, StockData


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_create_stock(db_session):
    stock = create_stock(db_session, "AAPL", "Apple Inc.", "Technology")
    assert stock.ticker == "AAPL"
    assert stock.name == "Apple Inc."


def test_get_stock(db_session):
    create_stock(db_session, "AAPL")
    stock = get_stock(db_session, "AAPL")
    assert stock is not None
    assert stock.ticker == "AAPL"


def test_store_prices(db_session):
    ohlcv_data = [
        OHLCV(
            date=datetime(2024, 1, 1),
            open=150.0, high=155.0, low=148.0, close=153.0,
            volume=1000000
        ),
        OHLCV(
            date=datetime(2024, 1, 2),
            open=153.0, high=158.0, low=151.0, close=156.0,
            volume=1200000
        ),
    ]
    stock_data = StockData(ticker="AAPL", data=ohlcv_data)

    count = store_prices(db_session, stock_data)
    assert count == 2


def test_store_prediction(db_session):
    prediction = store_prediction(
        db_session,
        "AAPL",
        "20240101_120000",
        155.0,
        153.0,
        1.31,
        days_ahead=1,
        metrics={"mae": 2.5, "r2": 0.85}
    )
    assert prediction.predicted_price == 155.0
    assert prediction.metrics["mae"] == 2.5
