import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session, abort

from core.db import get_db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT password_hash FROM usuarios WHERE username = ? AND ativo = 1",
                (username,),
            ).fetchone()
        finally:
            conn.close()
        if row is not None and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
            session["user"] = username
            return redirect(url_for("dashboard.index"))
        return abort(401)
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("dashboard.index"))
