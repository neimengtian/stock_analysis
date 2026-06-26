from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from .models import Stock, StockPrice, MLPrediction
from ..data.models import StockData


def create_stock(db: Session, ticker: str, name: Optional[str] = None, sector: Optional[str] = None) -> Stock:
    existing = db.query(Stock).filter(Stock.ticker == ticker).first()
    if existing:
        return existing

    stock = Stock(ticker=ticker, name=name, sector=sector)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


def get_stock(db: Session, ticker: str) -> Optional[Stock]:
    return db.query(Stock).filter(Stock.ticker == ticker).first()


def store_prices(db: Session, stock_data: StockData) -> int:
    stock = create_stock(db, stock_data.ticker)
    count = 0

    for ohlcv in stock_data.data:
        existing = db.query(StockPrice).filter(
            StockPrice.stock_id == stock.id,
            StockPrice.date == ohlcv.date
        ).first()

        if existing:
            continue

        price = StockPrice(
            stock_id=stock.id,
            date=ohlcv.date,
            open=ohlcv.open,
            high=ohlcv.high,
            low=ohlcv.low,
            close=ohlcv.close,
            volume=ohlcv.volume,
            adj_close=ohlcv.adj_close,
        )
        db.add(price)
        count += 1

    db.commit()
    return count


def get_prices(
    db: Session,
    ticker: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 1000,
) -> list[StockPrice]:
    stock = get_stock(db, ticker)
    if not stock:
        return []

    query = db.query(StockPrice).filter(StockPrice.stock_id == stock.id)

    if start_date:
        query = query.filter(StockPrice.date >= start_date)
    if end_date:
        query = query.filter(StockPrice.date <= end_date)

    return query.order_by(StockPrice.date.desc()).limit(limit).all()


def store_prediction(
    db: Session,
    ticker: str,
    model_version: str,
    predicted_price: float,
    current_price: float,
    predicted_change_pct: float,
    days_ahead: int = 1,
    metrics: Optional[dict] = None,
) -> MLPrediction:
    stock = create_stock(db, ticker)

    prediction = MLPrediction(
        stock_id=stock.id,
        model_version=model_version,
        predicted_price=predicted_price,
        current_price=current_price,
        predicted_change_pct=predicted_change_pct,
        days_ahead=days_ahead,
        metrics=metrics,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def get_predictions(
    db: Session,
    ticker: str,
    limit: int = 100,
) -> list[MLPrediction]:
    stock = get_stock(db, ticker)
    if not stock:
        return []

    return (
        db.query(MLPrediction)
        .filter(MLPrediction.stock_id == stock.id)
        .order_by(MLPrediction.created_at.desc())
        .limit(limit)
        .all()
    )
