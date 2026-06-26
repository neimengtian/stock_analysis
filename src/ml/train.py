import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ..data.fetcher import StockDataFetcher

logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self, models_dir: str = "src/ml/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def prepare_features(self, df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        df = df.copy()
        df["return_1d"] = df["close"].pct_change()
        df["return_5d"] = df["close"].pct_change(lookback)
        df["ma_5"] = df["close"].rolling(window=5).mean()
        df["ma_20"] = df["close"].rolling(window=20).mean()
        df["volatility_5"] = df["return_1d"].rolling(window=5).std()
        df["volume_ma_5"] = df["volume"].rolling(window=5).mean()
        df["high_low_range"] = (df["high"] - df["low"]) / df["close"]
        df["target"] = df["close"].shift(-1)
        df = df.dropna()
        return df

    def train(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        test_size: float = 0.2,
    ) -> dict:
        fetcher = StockDataFetcher()
        df = fetcher.fetch_to_dataframe(ticker, start_date, end_date)

        df = self.prepare_features(df)

        feature_columns = [
            "return_1d", "return_5d", "ma_5", "ma_20",
            "volatility_5", "volume_ma_5", "high_low_range"
        ]
        X = df[feature_columns]
        y = df["target"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)

        y_pred = model.predict(X_test_scaled)

        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

        model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.models_dir / f"{ticker}_model_{version}.pkl"
        scaler_path = self.models_dir / f"{ticker}_scaler_{version}.pkl"

        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)

        logger.info(f"Model saved: {model_path}")
        logger.info(f"Metrics: {metrics}")

        return {
            "ticker": ticker,
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
            "metrics": metrics,
            "feature_columns": feature_columns,
        }
