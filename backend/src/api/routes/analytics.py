from fastapi import APIRouter, Query

from src.api.config import settings
from src.api.schemas.responses import StockLevelAnalyticsItem, TrendPoint
from src.api.services.repository import fetch_prediction_trends, fetch_stock_level_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stock-levels", response_model=list[StockLevelAnalyticsItem])
def get_stock_level_analytics():
    return fetch_stock_level_analytics()


@router.get("/trends", response_model=list[TrendPoint])
def get_prediction_trends(days: int = Query(settings.default_trend_days, ge=1, le=30)):
    return fetch_prediction_trends(days=days)
