from __future__ import annotations

import logging
import os
import secrets

from backend.utils.paths import FRONTEND_DIR, INSTANCE_DIR

logger = logging.getLogger(__name__)

INSECURE_DEFAULT_SECRET_KEYS: set[str] = {
    "dev-only-change-me",
    "your-secret-key-here-change-in-production",
    "raahi-secret-key-fallback-2024",
    "secret",
    "changeme",
    "",
}


def get_secret_key() -> str:
    """Validate SECRET_KEY, warning in dev and generating a safe ephemeral fallback in production if unset."""
    key = os.getenv("SECRET_KEY", "").strip()
    is_production = bool(
        os.getenv("VERCEL")
        or os.getenv("RENDER")
        or os.getenv("FLASK_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
    )

    if not key or key in INSECURE_DEFAULT_SECRET_KEYS:
        if is_production:
            ephemeral_key = secrets.token_hex(32)
            logger.error(
                "CRITICAL: Production deployment detected without a persistent SECRET_KEY! "
                "Generated an ephemeral fallback (%s...). Session cookies will not persist across "
                "serverless cold starts. Please set SECRET_KEY in your Vercel Project Settings.",
                ephemeral_key[:8],
            )
            return ephemeral_key

        msg = (
            "SECURITY WARNING: Insecure or default SECRET_KEY is in use! "
            "Session cookies can be forged. Generate a strong key with `secrets.token_hex(32)`."
        )
        logger.warning("!" * 78)
        logger.warning(msg)
        logger.warning("!" * 78)
        return key or "dev-only-change-me"

    return key


def get_database_uri() -> str:
    """Resolve the database URI for the active environment."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        default_sqlite = f"sqlite:///{INSTANCE_DIR / 'raahi.db'}"
    else:
        default_sqlite = os.getenv("SQLITE_DATABASE_URI", "sqlite:///raahi.db")

    logger.warning(
        "CRITICAL: DATABASE_URL environment variable is not set. Falling back to local SQLite (%s). "
        "In production or serverless environments, this will result in ephemeral database storage.",
        default_sqlite,
    )
    return default_sqlite


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
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = get_engine_options(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    # Cookie and Session Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = bool(
        os.getenv("VERCEL")
        or os.getenv("RENDER")
        or os.getenv("FLASK_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
        or os.getenv("SESSION_COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
    )
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

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
