import logging
from datetime import datetime
from typing import Optional
from .celery_app import run_background

logger = logging.getLogger(__name__)


def fetch_stock_data_task(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    from ..data.fetcher import StockDataFetcher
    from ..storage.database import SessionLocal
    from ..storage.crud import store_prices
    import uuid

    task_id = str(uuid.uuid4())

    def _fetch():
        logger.info(f"Fetching data for {ticker}")
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        fetcher = StockDataFetcher()
        stock_data = fetcher.fetch(ticker, start, end)
        db = SessionLocal()
        try:
            count = store_prices(db, stock_data)
        finally:
            db.close()
        logger.info(f"Stored {count} prices for {ticker}")
        return {"ticker": ticker, "stored": count, "total": len(stock_data.data)}

    run_background(task_id, _fetch)
    return task_id


def fetch_multiple_stocks_task(
    tickers: list[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    from ..data.fetcher import StockDataFetcher
    from ..storage.database import SessionLocal
    from ..storage.crud import store_prices
    import uuid

    task_id = str(uuid.uuid4())

    def _fetch():
        logger.info(f"Fetching data for {len(tickers)} tickers")
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        fetcher = StockDataFetcher()
        results = {}
        db = SessionLocal()
        try:
            for ticker in tickers:
                try:
                    stock_data = fetcher.fetch(ticker, start, end)
                    count = store_prices(db, stock_data)
                    results[ticker] = {"stored": count, "total": len(stock_data.data)}
                except Exception as e:
                    logger.error(f"Failed to fetch {ticker}: {e}")
                    results[ticker] = {"error": str(e)}
        finally:
            db.close()
        return results

    run_background(task_id, _fetch)
    return task_id
