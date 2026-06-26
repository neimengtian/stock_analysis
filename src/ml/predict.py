import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from ..data.fetcher import StockDataFetcher
from .train import ModelTrainer

logger = logging.getLogger(__name__)


class ModelPredictor:
    def __init__(self, models_dir: str = "src/ml/models"):
        self.models_dir = Path(models_dir)
        self.trainer = ModelTrainer(models_dir)

    def load_model(self, ticker: str, model_version: Optional[str] = None):
        if model_version is None:
            model_files = sorted(self.models_dir.glob(f"{ticker}_model_*.pkl"))
            if not model_files:
                raise FileNotFoundError(f"No model found for {ticker}")
            model_path = model_files[-1]
        else:
            model_path = self.models_dir / f"{ticker}_model_{model_version}.pkl"

        scaler_path = model_path.parent / model_path.name.replace("model", "scaler")

        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)

        return model, scaler

    def predict(
        self,
        ticker: str,
        days_ahead: int = 1,
        model_version: Optional[str] = None,
    ) -> dict:
        fetcher = StockDataFetcher()
        df = fetcher.fetch_to_dataframe(ticker, period="6mo")

        df = self.trainer.prepare_features(df)

        model, scaler = self.load_model(ticker, model_version)

        feature_columns = [
            "return_1d", "return_5d", "ma_5", "ma_20",
            "volatility_5", "volume_ma_5", "high_low_range"
        ]
        X = df[feature_columns].iloc[[-1]]
        X_scaled = scaler.transform(X)

        prediction = model.predict(X_scaled)[0]
        current_price = df["close"].iloc[-1]

        return {
            "ticker": ticker,
            "current_price": current_price,
            "predicted_price": round(prediction, 2),
            "predicted_change_pct": round((prediction - current_price) / current_price * 100, 2),
            "days_ahead": days_ahead,
            "model_version": model_version or "latest",
            "prediction_time": datetime.now().isoformat(),
        }

    def predict_batch(
        self,
        tickers: list[str],
        model_version: Optional[str] = None,
    ) -> list[dict]:
        results = []
        for ticker in tickers:
            try:
                result = self.predict(ticker, model_version=model_version)
                results.append(result)
            except Exception as e:
                logger.error(f"Prediction failed for {ticker}: {e}")
                results.append({"ticker": ticker, "error": str(e)})
        return results
