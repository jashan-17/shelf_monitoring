import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
DEFAULT_MODEL_PATH = BACKEND_ROOT / "models" / "model_v2.tflite"
FALLBACK_MODEL_PATH = BACKEND_ROOT / "models" / "model.tflite"


def _get_env(name: str, default: str | None = None, *, required: bool = False) -> str:
    value = os.getenv(name, default)
    if value is None or not str(value).strip():
        if required:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return ""
    return str(value).strip()


def _get_int_env(name: str, default: int) -> int:
    raw_value = _get_env(name, str(default))
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer.") from exc


def _normalize_database_url(url: str) -> str:
    normalized_url = url.replace("postgres://", "postgresql://", 1)
    parts = urlsplit(normalized_url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))

    # External managed PostgreSQL services often require TLS in production.
    query_params.setdefault("sslmode", _get_env("DATABASE_SSLMODE", "require"))

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query_params),
            parts.fragment,
        )
    )


def _get_cors_origins():
    raw_origins = _get_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


class Settings:
    app_name = "Shelf Monitoring API"
    api_prefix = "/api"
    cors_origins = _get_cors_origins()
    database_url = _normalize_database_url(_get_env("DATABASE_URL", required=True))
    database_connect_timeout = _get_int_env("DATABASE_CONNECT_TIMEOUT", 10)
    _raw_model_path = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
    _raw_fallback_model_path = Path(os.getenv("FALLBACK_MODEL_PATH", str(FALLBACK_MODEL_PATH)))
    model_path = _raw_model_path if _raw_model_path.is_absolute() else PROJECT_ROOT / _raw_model_path
    fallback_model_path = (
        _raw_fallback_model_path
        if _raw_fallback_model_path.is_absolute()
        else PROJECT_ROOT / _raw_fallback_model_path
    )
    default_prediction_limit = _get_int_env("DEFAULT_PREDICTION_LIMIT", 10)
    default_trend_days = _get_int_env("DEFAULT_TREND_DAYS", 7)


settings = Settings()
