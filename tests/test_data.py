import pytest
from datetime import datetime, timedelta
from src.data.fetcher import StockDataFetcher
from src.data.models import OHLCV, StockData


@pytest.fixture
def fetcher():
    return StockDataFetcher()


def test_fetch_returns_stock_data(fetcher):
    ticker = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    result = fetcher.fetch(ticker, start_date=start_date, end_date=end_date)

    assert isinstance(result, StockData)
    assert result.ticker == ticker
    assert len(result.data) > 0
    assert all(isinstance(d, OHLCV) for d in result.data)


def test_fetch_to_dataframe(fetcher):
    ticker = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    df = fetcher.fetch_to_dataframe(ticker, start_date=start_date, end_date=end_date)

    assert len(df) > 0
    assert "open" in df.columns
    assert "high" in df.columns
    assert "low" in df.columns
    assert "close" in df.columns
    assert "volume" in df.columns
