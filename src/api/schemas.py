from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StockCreate(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None


class StockResponse(BaseModel):
    id: int
    ticker: str
    name: Optional[str]
    sector: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PriceResponse(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float]

    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    ticker: str
    days_ahead: int = 1


class PredictionResponse(BaseModel):
    ticker: str
    current_price: float
    predicted_price: float
    predicted_change_pct: float
    days_ahead: int
    model_version: str
    prediction_time: str


class TrainRequest(BaseModel):
    ticker: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class TrainResponse(BaseModel):
    ticker: str
    model_path: str
    metrics: dict
    feature_columns: list[str]
