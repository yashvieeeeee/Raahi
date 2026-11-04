from backend.database.extensions import db, limiter, login_manager


def init_extensions(app) -> None:
    """Attach shared Flask extensions to the application."""
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
