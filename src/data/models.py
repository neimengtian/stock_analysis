from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OHLCV:
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None


@dataclass
class StockData:
    ticker: str
    data: list[OHLCV]
    source: str = "yfinance"
    fetched_at: Optional[datetime] = None
