from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PredictionRecord(BaseModel):
    id: int
    image_name: str
    actual_label: Optional[str] = None
    predicted_label: str
    confidence: float
    created_at: datetime


class PredictionResult(BaseModel):
    image_name: str
    predicted_label: str
    confidence: float
    probabilities: dict[str, float]
    saved_to_database: bool = False


class SavePredictionRequest(BaseModel):
    image_name: str
    predicted_label: str
    confidence: float
    actual_label: Optional[str] = None


class SavePredictionResponse(BaseModel):
    message: str
    prediction: PredictionRecord
