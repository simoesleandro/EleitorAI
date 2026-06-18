from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.veritas import bp as veritas_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(veritas_bp)
