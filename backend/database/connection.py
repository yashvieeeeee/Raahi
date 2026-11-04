from backend.database.extensions import db, limiter, login_manager


def init_extensions(app) -> None:
    """Attach shared Flask extensions to the application."""
    try:
        db.init_app(app)
    except Exception as exc:
        app.logger.error("Failed to initialize database extension: %s", exc)
    login_manager.init_app(app)
    limiter.init_app(app)
