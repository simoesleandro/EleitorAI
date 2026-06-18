from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
