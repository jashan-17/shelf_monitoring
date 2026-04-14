import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
DEFAULT_MODEL_PATH = BACKEND_ROOT / "models" / "model.keras"
FALLBACK_MODEL_PATH = BACKEND_ROOT / "models" / "model.h5"


def _get_cors_origins():
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


class Settings:
    app_name = "Shelf Monitoring API"
    api_prefix = "/api"
    cors_origins = _get_cors_origins()
    _raw_model_path = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
    _raw_fallback_model_path = Path(os.getenv("FALLBACK_MODEL_PATH", str(FALLBACK_MODEL_PATH)))
    model_path = _raw_model_path if _raw_model_path.is_absolute() else PROJECT_ROOT / _raw_model_path
    fallback_model_path = (
        _raw_fallback_model_path
        if _raw_fallback_model_path.is_absolute()
        else PROJECT_ROOT / _raw_fallback_model_path
    )
    default_prediction_limit = int(os.getenv("DEFAULT_PREDICTION_LIMIT", "10"))
    default_trend_days = int(os.getenv("DEFAULT_TREND_DAYS", "7"))


settings = Settings()
