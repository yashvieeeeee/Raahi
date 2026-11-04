import logging
import os

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.database.extensions import db
from backend.database.models import User
from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)


def _get_admin_credentials() -> tuple[str, str]:
    """Retrieve admin credentials from environment, requiring non-empty ADMIN_PASSWORD."""
    email = os.getenv("ADMIN_EMAIL", "admin@raahi.local").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    return email, password


def _normalize_identity(value):
    normalized = (value or "").strip()
    if "@" in normalized:
        return normalized.lower()
    return normalized


def register_user(name, email_or_phone, password):
    normalized_identity = _normalize_identity(email_or_phone)
    admin_email, _ = _get_admin_credentials()

    if admin_email and normalized_identity == admin_email:
        return None, "Admin account cannot be registered from signup"

    try:
        existing_user = User.query.filter(
            (User.email == normalized_identity) | (User.phone == normalized_identity)
        ).first()
        if existing_user:
            return None, "Email or phone already registered"

        user = User(
            name=(name or "").strip(),
            email=normalized_identity if "@" in normalized_identity else None,
            phone=normalized_identity if "@" not in normalized_identity else None,
            password_hash=generate_password_hash(password),
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.error("Database error during registration: %s", exc)
        return None, "Database service is temporarily unavailable. Please try again shortly."

    try:
        notification_service.send_welcome_message(normalized_identity, user.name)
    except Exception as exc:
        logger.warning("Could not send welcome message: %s", exc)

    return user, None


def authenticate_user(email_or_phone, password):
    normalized_identity = _normalize_identity(email_or_phone)
    admin_email, admin_password = _get_admin_credentials()

    try:
        # Check if login attempt is for admin identity
        if admin_email and normalized_identity == admin_email:
            if not admin_password:
                logger.error(
                    "Admin login attempted for '%s' but ADMIN_PASSWORD is not set in the environment.",
                    admin_email,
                )
                return None, "Admin login is disabled because ADMIN_PASSWORD is not set in environment."

            if password != admin_password:
                return None, "Invalid credentials"

            admin_user = User.query.filter_by(email=admin_email).first()
            if not admin_user:
                admin_user = User(
                    name="Admin",
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    is_admin=True,
                )
                db.session.add(admin_user)
                db.session.commit()
            elif not admin_user.is_admin or not check_password_hash(admin_user.password_hash, admin_password):
                admin_user.is_admin = True
                admin_user.password_hash = generate_password_hash(admin_password)
                db.session.commit()
            return admin_user, None

        # Standard commuter user authentication
        user = User.query.filter(
            (User.email == normalized_identity) | (User.phone == normalized_identity)
        ).first()
        if user and check_password_hash(user.password_hash, password):
            return user, None
        return None, None
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.error("Database error during authentication: %s", exc)
        return None, "Database service is temporarily unavailable. Please try again shortly."
