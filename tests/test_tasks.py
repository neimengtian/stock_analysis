import pytest
from unittest.mock import patch, MagicMock
from src.tasks.celery_app import run_background, get_task_result
from src.tasks.ml_tasks import train_model_task, predict_task
from src.tasks.data_tasks import fetch_stock_data_task


def test_run_background():
    def simple_task():
        return "done"

    task_id = run_background("test-123", simple_task)
    assert task_id == "test-123"


def test_get_task_result():
    result = get_task_result("nonexistent")
    assert result["status"] == "unknown"


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

    task_id = train_model_task("AAPL")
    assert task_id is not None


@patch("src.tasks.data_tasks.StockDataFetcher")
def test_fetch_stock_data_task(mock_fetcher):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = MagicMock(data=[])
    mock_fetcher.return_value = mock_instance

    with patch("src.tasks.data_tasks.SessionLocal"):
        with patch("src.tasks.data_tasks.store_prices", return_value=0):
            task_id = fetch_stock_data_task("AAPL")

    assert task_id is not None
