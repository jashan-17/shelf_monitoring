from fastapi import APIRouter, Query

from src.api.config import settings
from src.api.schemas.responses import (
    PredictionRecord,
    SavePredictionRequest,
    SavePredictionResponse,
)
from src.api.services.repository import fetch_latest_predictions, insert_single_prediction

router = APIRouter(tags=["predictions"])


@router.get("/predictions", response_model=list[PredictionRecord])
def get_predictions(limit: int = Query(settings.default_prediction_limit, ge=1, le=100)):
    return fetch_latest_predictions(limit=limit)


@router.post("/predictions/save", response_model=SavePredictionResponse)
def save_prediction(payload: SavePredictionRequest):
    saved_prediction = insert_single_prediction(
        image_name=payload.image_name,
        predicted_label=payload.predicted_label,
        confidence=payload.confidence,
        actual_label=payload.actual_label,
    )
    return {
        "message": "Prediction saved to PostgreSQL successfully.",
        "prediction": saved_prediction,
    }
