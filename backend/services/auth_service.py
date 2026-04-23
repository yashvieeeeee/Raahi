import os

from werkzeug.security import check_password_hash, generate_password_hash

from backend.database.extensions import db
from backend.database.models import User
from backend.services.notification_service import notification_service


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@raahi.local").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def _normalize_identity(value):
    normalized = (value or "").strip()
    if "@" in normalized:
        return normalized.lower()
    return normalized


def register_user(name, email_or_phone, password):
    normalized_identity = _normalize_identity(email_or_phone)

    if ADMIN_EMAIL and normalized_identity == ADMIN_EMAIL:
        return None, "Admin account cannot be registered from signup"

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

    try:
        notification_service.send_welcome_message(normalized_identity, user.name)
    except Exception as exc:
        print(f"Could not send welcome message: {exc}")

    return user, None


def authenticate_user(email_or_phone, password):
    normalized_identity = _normalize_identity(email_or_phone)

    if ADMIN_EMAIL and ADMIN_PASSWORD and normalized_identity == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                name="Admin",
                email=ADMIN_EMAIL,
                password_hash=generate_password_hash(ADMIN_PASSWORD),
                is_admin=True,
            )
            db.session.add(admin_user)
            db.session.commit()
        elif not admin_user.is_admin:
            admin_user.is_admin = True
            admin_user.password_hash = generate_password_hash(ADMIN_PASSWORD)
            db.session.commit()
        return admin_user

    user = User.query.filter(
        (User.email == normalized_identity) | (User.phone == normalized_identity)
    ).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
