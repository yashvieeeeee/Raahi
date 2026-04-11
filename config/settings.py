from __future__ import annotations

import os

from backend.utils.paths import FRONTEND_DIR, INSTANCE_DIR


def get_database_uri() -> str:
    """Resolve the database URI for the active environment."""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL", "")

    return os.getenv("SQLITE_DATABASE_URI", "sqlite:///raahi.db")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "raahi-secret-key-fallback-2024")
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    GOOGLE_MAPS_API_KEY = os.getenv(
        "GOOGLE_MAPS_API_KEY",
        "AIzaSyBZrGSUuzA_dD8-nMgyn7QKwnzVc4oZ6Y8",
    )
    OPENAQ_API_KEY = os.getenv(
        "OPENAQ_API_KEY",
        "dd21323edb344e82705f102b9cb4dc67d2d8024f1e0c826f0a60a6ddebc9c013",
    )
    WAQI_API_TOKEN = os.getenv(
        "WAQI_API_TOKEN",
        "b4b0e7942a8e443d74e2288115b62dd43366996c",
    )
    PDF_EXPORT_SERVICE_URL = os.getenv(
        "PDF_EXPORT_SERVICE_URL",
        "http://127.0.0.1:3001",
    )

    TEMPLATES_FOLDER = str(FRONTEND_DIR / "templates")
    STATIC_FOLDER = str(FRONTEND_DIR / "static")
    INSTANCE_PATH = str(INSTANCE_DIR)
