from flask import Flask
from flask_wtf.csrf import CSRFProtect

from core.config import get_settings

csrf = CSRFProtect()


def create_app() -> Flask:
    settings = get_settings()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["DB_PATH"] = settings.db_path

    csrf.init_app(app)

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
