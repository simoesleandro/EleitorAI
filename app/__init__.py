from flask import Flask

from core.config import get_settings


def create_app() -> Flask:
    settings = get_settings()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["DB_PATH"] = settings.db_path

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
