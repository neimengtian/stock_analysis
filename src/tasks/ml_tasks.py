import logging
from datetime import datetime
from typing import Optional
from .celery_app import run_background

logger = logging.getLogger(__name__)


def train_model_task(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    from ..ml.train import ModelTrainer
    import uuid

    task_id = str(uuid.uuid4())

    def _train():
        logger.info(f"Starting training for {ticker}")
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        trainer = ModelTrainer()
        result = trainer.train(ticker, start, end)
        logger.info(f"Training completed for {ticker}: {result['metrics']}")
        return result

    run_background(task_id, _train)
    return task_id


def predict_task(
    ticker: str,
    days_ahead: int = 1,
    model_version: Optional[str] = None,
) -> str:
    from ..ml.predict import ModelPredictor
    from ..storage.database import SessionLocal
    from ..storage.crud import store_prediction
    import uuid

    task_id = str(uuid.uuid4())

    def _predict():
        logger.info(f"Starting prediction for {ticker}")
        predictor = ModelPredictor()
        result = predictor.predict(ticker, days_ahead, model_version)
        db = SessionLocal()
        try:
            store_prediction(
                db,
                ticker=result["ticker"],
                model_version=result["model_version"],
                predicted_price=result["predicted_price"],
                current_price=result["current_price"],
                predicted_change_pct=result["predicted_change_pct"],
                days_ahead=result["days_ahead"],
            )
        finally:
            db.close()
        logger.info(f"Prediction completed for {ticker}: {result['predicted_price']}")
        return result

    run_background(task_id, _predict)
    return task_id
