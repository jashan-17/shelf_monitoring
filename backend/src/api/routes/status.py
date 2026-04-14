from fastapi import APIRouter

from src.api.schemas.responses import SystemStatusResponse
from src.api.services.repository import check_database_status

router = APIRouter(tags=["status"])


@router.get("/status", response_model=SystemStatusResponse, response_model_by_alias=False)
def get_system_status():
    database_ok = False
    try:
        database_ok = check_database_status()
    except Exception:
        database_ok = False

    return {
        "database": {
            "label": "Database",
            "status": "online" if database_ok else "offline",
            "detail": "Connected to PostgreSQL." if database_ok else "Connection check failed.",
        },
        "airflow": {
            "label": "Airflow",
            "status": "placeholder",
            "detail": "Placeholder card ready for DAG run status integration.",
        },
        "dbt_pipeline": {
            "label": "dbt Pipeline",
            "status": "placeholder",
            "detail": "Placeholder card ready for dbt run metadata integration.",
        },
    }
