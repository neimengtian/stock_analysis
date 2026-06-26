from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...storage.database import get_db
from ...storage.crud import create_stock, get_stock, store_prices, get_prices
from ...data.fetcher import StockDataFetcher
from ...tasks.data_tasks import fetch_stock_data_task
from ..schemas import StockCreate, StockResponse, PriceResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/", response_model=StockResponse)
def create_stock_endpoint(stock_data: StockCreate, db: Session = Depends(get_db)):
    stock = create_stock(db, stock_data.ticker, stock_data.name, stock_data.sector)
    return stock


@router.get("/{ticker}", response_model=StockResponse)
def get_stock_endpoint(ticker: str, db: Session = Depends(get_db)):
    stock = get_stock(db, ticker)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
    return stock


@router.get("/{ticker}/prices", response_model=list[PriceResponse])
def get_prices_endpoint(
    ticker: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    prices = get_prices(db, ticker, start_date, end_date, limit)
    return prices


@router.post("/{ticker}/fetch")
def fetch_and_store_endpoint(
    ticker: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    fetcher = StockDataFetcher()
    try:
        stock_data = fetcher.fetch(ticker, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    count = store_prices(db, stock_data)
    return {"ticker": ticker, "stored": count, "total": len(stock_data.data)}


@router.post("/{ticker}/fetch/async")
def fetch_and_store_async_endpoint(
    ticker: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    start = start_date.isoformat() if start_date else None
    end = end_date.isoformat() if end_date else None

    task = fetch_stock_data_task.delay(ticker, start, end)
    return {"task_id": task.id, "status": "submitted", "ticker": ticker}
