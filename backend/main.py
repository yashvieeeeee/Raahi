from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException


if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.database.connection import init_extensions
from backend.database.extensions import db, login_manager
from backend.database.models import User
from backend.routes.admin_routes import register_admin_routes
from backend.routes.api_routes import register_api_routes
from backend.routes.auth_routes import register_auth_routes
from backend.routes.ml_routes import ml_blueprint
from backend.routes.web_routes import register_web_routes
from config.settings import Config


load_dotenv()


def create_app():
    app = Flask(
        __name__,
        template_folder=Config.TEMPLATES_FOLDER,
        static_folder=Config.STATIC_FOLDER,
        instance_path=Config.INSTANCE_PATH,
        instance_relative_config=True,
    )
    app.config.from_object(Config)

    init_extensions(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    register_auth_routes(app)
    register_web_routes(app)
    register_api_routes(app)
    register_admin_routes(app)
    app.register_blueprint(ml_blueprint)

    @app.errorhandler(429)
    def handle_429_error(error):
        description = getattr(error, "description", "Too many requests. Please slow down.")
        if request.path.startswith("/api/"):
            return jsonify({
                "status": "error",
                "message": f"Rate limit exceeded: {description}"
            }), 429

        return (
            "<!DOCTYPE html><html><head><title>429 - Too Many Requests</title></head>"
            "<body style='font-family:sans-serif;text-align:center;padding:50px;'>"
            "<h1>Too Many Requests</h1>"
            f"<p>{description}</p>"
            "<p>Please wait a moment and try again.</p>"
            "<a href='/'>Return to Home</a></body></html>"
        ), 429

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def handle_500_error(error):
        if isinstance(error, HTTPException) and error.code != 500:
            return error

        try:
            db.session.rollback()
        except Exception:
            pass

        app.logger.error("Internal Server Error: %s", error, exc_info=True)

        if request.path.startswith("/api/"):
            return jsonify({
                "status": "error",
                "message": "An internal server error occurred. Please try again later."
            }), 500

        try:
            return render_template("500.html"), 500
        except Exception:
            return (
                "<!DOCTYPE html><html><head><title>500 - Server Error</title></head>"
                "<body style='font-family:sans-serif;text-align:center;padding:50px;'>"
                "<h1>Service Temporarily Unavailable</h1>"
                "<p>Raahi is experiencing a temporary issue. Please try again shortly.</p>"
                "<a href='/'>Return to Home</a></body></html>"
            ), 500

    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:
            app.logger.error("Database initialization failed: %s", exc)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
