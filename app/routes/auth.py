import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session, abort

from core.config import get_settings

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        settings = get_settings()
        if username == "admin" and _check_password(password, settings.admin_pass):
            session["user"] = username
            return redirect(url_for("dashboard.index"))
        return abort(401)
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("dashboard.index"))


def _check_password(plain: str, hashed_or_plain: str) -> bool:
    if hashed_or_plain.startswith("$2"):
        return bcrypt.checkpw(plain.encode(), hashed_or_plain.encode())
    return plain == hashed_or_plain
