import pytest
from unittest.mock import patch, MagicMock
from src.tasks.celery_app import celery_app
from src.tasks.ml_tasks import train_model_task, predict_task
from src.tasks.data_tasks import fetch_stock_data_task


def test_celery_app_config():
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.enable_utc is True


@patch("src.tasks.ml_tasks.ModelTrainer")
def test_train_model_task(mock_trainer):
    mock_instance = MagicMock()
    mock_instance.train.return_value = {
        "ticker": "AAPL",
        "model_path": "test.pkl",
        "metrics": {"mae": 1.0},
        "feature_columns": ["return_1d"],
    }
    mock_trainer.return_value = mock_instance

    result = train_model_task("AAPL")

    assert result["ticker"] == "AAPL"
    mock_instance.train.assert_called_once()


@patch("src.tasks.data_tasks.StockDataFetcher")
def test_fetch_stock_data_task(mock_fetcher):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = MagicMock(data=[])
    mock_fetcher.return_value = mock_instance

    with patch("src.tasks.data_tasks.SessionLocal"):
        with patch("src.tasks.data_tasks.store_prices", return_value=0):
            result = fetch_stock_data_task("AAPL")

    assert result["ticker"] == "AAPL"
