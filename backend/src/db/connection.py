import logging

import psycopg2

from src.api.config import settings

logger = logging.getLogger(__name__)


class DatabaseConnectionError(RuntimeError):
    pass


def get_connection():
    try:
        return psycopg2.connect(
            settings.database_url,
            connect_timeout=settings.database_connect_timeout,
            application_name="shelf-monitoring-api",
        )
    except psycopg2.OperationalError as exc:
        logger.exception("PostgreSQL connection failed.")
        raise DatabaseConnectionError(
            "Unable to connect to PostgreSQL. Verify DATABASE_URL, SSL settings, and network access."
        ) from exc
