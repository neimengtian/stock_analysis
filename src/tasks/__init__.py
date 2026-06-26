from .celery_app import celery_app
from .ml_tasks import train_model_task, predict_task
from .data_tasks import fetch_stock_data_task

__all__ = [
    "celery_app",
    "train_model_task",
    "predict_task",
    "fetch_stock_data_task",
]
