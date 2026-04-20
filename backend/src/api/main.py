from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import settings
from src.api.routes.analytics import router as analytics_router
from src.api.routes.predict import router as predict_router
from src.api.routes.predictions import router as predictions_router
from src.api.routes.status import router as status_router
from src.api.routes.summary import router as summary_router
from src.db.connection import DatabaseConnectionError

app = FastAPI(title=settings.app_name)

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


@app.get("/")
def root():
    return {"message": "Shelf Monitoring API is running."}


app.include_router(summary_router, prefix=settings.api_prefix)
app.include_router(predictions_router, prefix=settings.api_prefix)
app.include_router(predict_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(status_router, prefix=settings.api_prefix)
