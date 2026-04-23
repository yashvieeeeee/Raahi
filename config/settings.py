from __future__ import annotations

import os

from backend.utils.paths import FRONTEND_DIR, INSTANCE_DIR


def get_database_uri() -> str:
    """Resolve the database URI for the active environment."""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL", "")

    return os.getenv("SQLITE_DATABASE_URI", "sqlite:///raahi.db")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = get_database_uri()
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
