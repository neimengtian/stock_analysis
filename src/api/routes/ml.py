from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...storage.database import get_db
from ...storage.crud import store_prediction
from ...ml.train import ModelTrainer
from ...ml.predict import ModelPredictor
from ...tasks.ml_tasks import train_model_task, predict_task
from ...tasks.celery_app import get_task_result
from ..schemas import (
    TrainRequest, TrainResponse,
    PredictionRequest, PredictionResponse,
)

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/train", response_model=TrainResponse)
def train_model_endpoint(request: TrainRequest):
    trainer = ModelTrainer()
    try:
        result = trainer.train(request.ticker, request.start_date, request.end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TrainResponse(
        ticker=result["ticker"],
        model_path=result["model_path"],
        metrics=result["metrics"],
        feature_columns=result["feature_columns"],
    )


@router.post("/train/background")
def train_model_background_endpoint(request: TrainRequest):
    start_date = request.start_date.isoformat() if request.start_date else None
    end_date = request.end_date.isoformat() if request.end_date else None
    task_id = train_model_task(request.ticker, start_date, end_date)
    return {"task_id": task_id, "status": "submitted", "ticker": request.ticker}


@router.post("/predict", response_model=PredictionResponse)
def predict_endpoint(request: PredictionRequest, db: Session = Depends(get_db)):
    predictor = ModelPredictor()
    try:
        result = predictor.predict(request.ticker, request.days_ahead)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    store_prediction(
        db,
        ticker=result["ticker"],
        model_version=result["model_version"],
        predicted_price=result["predicted_price"],
        current_price=result["current_price"],
        predicted_change_pct=result["predicted_change_pct"],
        days_ahead=result["days_ahead"],
    )

    return PredictionResponse(**result)


@router.post("/predict/background")
def predict_background_endpoint(request: PredictionRequest):
    task_id = predict_task(request.ticker, request.days_ahead)
    return {"task_id": task_id, "status": "submitted", "ticker": request.ticker}


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = get_task_result(task_id)
    return {"task_id": task_id, **result}
