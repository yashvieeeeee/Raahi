from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask


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

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
