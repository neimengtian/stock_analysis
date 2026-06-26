import pytest
from datetime import datetime, timedelta
from src.ml.train import ModelTrainer
from src.ml.predict import ModelPredictor


@pytest.fixture
def trainer():
    return ModelTrainer(models_dir="tests/test_models")


@pytest.fixture
def predictor():
    return ModelPredictor(models_dir="tests/test_models")


def test_prepare_features(trainer):
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(100, 200, 30),
        "high": np.random.uniform(100, 200, 30),
        "low": np.random.uniform(100, 200, 30),
        "close": np.random.uniform(100, 200, 30),
        "volume": np.random.randint(1000000, 5000000, 30),
    })

    result = trainer.prepare_features(df)

    assert "return_1d" in result.columns
    assert "ma_5" in result.columns
    assert "target" in result.columns
    assert len(result) > 0


def test_train_model(trainer):
    ticker = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    result = trainer.train(ticker, start_date=start_date, end_date=end_date)

    assert "model_path" in result
    assert "metrics" in result
    assert "mae" in result["metrics"]
    assert "r2" in result["metrics"]


def test_predict(predictor):
    ticker = "AAPL"
    result = predictor.predict(ticker)

    assert "ticker" in result
    assert "current_price" in result
    assert "predicted_price" in result
    assert "predicted_change_pct" in result
