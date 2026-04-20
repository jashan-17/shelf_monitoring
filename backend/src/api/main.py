import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.config import settings
from src.api.routes.predict import router as predict_router
from src.api.routes.predictions import router as predictions_router
from src.api.services.inference import InvalidImageError, ModelUnavailableError, preload_model
from src.db.connection import DatabaseConnectionError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not preload_model():
        logger.warning("Model preload failed. Prediction endpoint will return 503 until a model is available.")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DatabaseConnectionError)
def handle_database_connection_error(_request: Request, exc: DatabaseConnectionError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
            "error": "database_unavailable",
        },
    )


@app.exception_handler(ModelUnavailableError)
def handle_model_unavailable(_request: Request, exc: ModelUnavailableError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
            "error": "model_unavailable",
        },
    )


@app.exception_handler(InvalidImageError)
def handle_invalid_image(_request: Request, exc: InvalidImageError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error": "invalid_image",
        },
    )


@app.get("/")
def root():
    return {"message": "Shelf Monitoring API is running."}


app.include_router(predictions_router, prefix=settings.api_prefix)
app.include_router(predict_router, prefix=settings.api_prefix)
