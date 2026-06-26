import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from .models import OHLCV, StockData

logger = logging.getLogger(__name__)


class StockDataFetcher:
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir

    def fetch(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "1y",
    ) -> StockData:
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        logger.info(f"Fetching {ticker} from {start_date.date()} to {end_date.date()}")

        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, period=period)

        if df.empty:
            raise ValueError(f"No data returned for ticker {ticker}")

        ohlcv_data = [
            OHLCV(
                date=row.name.to_pydatetime(),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"]),
                adj_close=row.get("Adj Close"),
            )
            for row in df.itertuples()
        ]

        return StockData(
            ticker=ticker,
            data=ohlcv_data,
            source="yfinance",
            fetched_at=datetime.now(),
        )

    def fetch_to_dataframe(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "1y",
    ) -> pd.DataFrame:
        stock_data = self.fetch(ticker, start_date, end_date, period)
        return pd.DataFrame([
            {
                "date": ohlcv.date,
                "open": ohlcv.open,
                "high": ohlcv.high,
                "low": ohlcv.low,
                "close": ohlcv.close,
                "volume": ohlcv.volume,
                "adj_close": ohlcv.adj_close,
            }
            for ohlcv in stock_data.data
        ])

    def fetch_multiple(
        self,
        tickers: list[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "1y",
    ) -> dict[str, StockData]:
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = self.fetch(ticker, start_date, end_date, period)
            except Exception as e:
                logger.error(f"Failed to fetch {ticker}: {e}")
                results[ticker] = None
        return results
