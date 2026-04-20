from src.api.schemas.responses import (
    SavePredictionRequest,
    SavePredictionResponse,
)
from src.api.services.repository import insert_single_prediction

router = APIRouter(tags=["predictions"])


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
