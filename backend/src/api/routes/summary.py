from fastapi import APIRouter

from src.api.schemas.responses import SummaryResponse
from src.api.services.repository import fetch_summary

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary():
    return fetch_summary()
