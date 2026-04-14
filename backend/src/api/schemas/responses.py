from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CountsByClass(BaseModel):
    empty: int = 0
    low: int = 0
    medium: int = 0
    full: int = 0


class SummaryResponse(BaseModel):
    total_predictions: int
    counts_by_class: CountsByClass
    average_confidence: float


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


class StockLevelAnalyticsItem(BaseModel):
    stock_level: str
    total_images: int
    avg_confidence: float


class TrendPoint(BaseModel):
    date: str
    empty: int = 0
    low: int = 0
    medium: int = 0
    full: int = 0


class ServiceStatus(BaseModel):
    label: str
    status: str
    detail: str


class SystemStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    database: ServiceStatus
    airflow: ServiceStatus
    dbt: ServiceStatus = Field(alias="dbt_pipeline")
