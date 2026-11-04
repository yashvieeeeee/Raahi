from __future__ import annotations

import logging
import os

from backend.utils.paths import FRONTEND_DIR, INSTANCE_DIR

logger = logging.getLogger(__name__)


def get_database_uri() -> str:
    """Resolve the database URI for the active environment."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    logger.warning(
        "CRITICAL: DATABASE_URL environment variable is not set. Falling back to local SQLite (%s). "
        "In production or serverless environments, this will result in database connection failures.",
        os.getenv("SQLITE_DATABASE_URI", "sqlite:///raahi.db"),
    )
    return os.getenv("SQLITE_DATABASE_URI", "sqlite:///raahi.db")


def get_engine_options(database_uri: str) -> dict:
    """Return database engine options tuned for connection resilience."""
    options = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    if database_uri.startswith("postgresql"):
        options["connect_args"] = {"connect_timeout": 5}
    elif database_uri.startswith("sqlite"):
        options["connect_args"] = {"timeout": 5}
    return options


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = get_engine_options(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "")
    WAQI_API_TOKEN = os.getenv("WAQI_API_TOKEN", "")
    PDF_EXPORT_SERVICE_URL = os.getenv(
        "PDF_EXPORT_SERVICE_URL",
        "http://127.0.0.1:3001",
    )

    TEMPLATES_FOLDER = str(FRONTEND_DIR / "templates")
    STATIC_FOLDER = str(FRONTEND_DIR / "static")
    INSTANCE_PATH = str(INSTANCE_DIR)
