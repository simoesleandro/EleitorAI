from flask import Flask
from flask_wtf.csrf import CSRFProtect

from core.config import get_settings
from core.db import get_db
from core.logging_redactor import install_redactor

csrf = CSRFProtect()

install_redactor()


def _kpi_context() -> dict:
    try:
        conn = get_db()
        try:
            checagens = conn.execute("SELECT COUNT(*) AS c FROM checagens").fetchone()["c"]
            queue_pending = conn.execute("SELECT COUNT(*) AS c FROM job_queue WHERE status = 'pending'").fetchone()["c"]
            alertas = conn.execute("SELECT COUNT(*) AS c FROM alertas WHERE enviado_telegram = 1").fetchone()["c"]
        finally:
            conn.close()
    except Exception:
        checagens = 0
        queue_pending = 0
        alertas = 0
    return {"kpi": {"checagens": checagens, "queue_pending": queue_pending, "alertas": alertas}}


def create_app() -> Flask:
    settings = get_settings()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["DB_PATH"] = settings.db_path
    app.config["WTF_CSRF_TIME_LIMIT"] = None

    csrf.init_app(app)
    app.context_processor(_kpi_context)

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
