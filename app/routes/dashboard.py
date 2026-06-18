from flask import Blueprint, render_template, redirect, url_for, jsonify

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def root():
    return redirect(url_for("dashboard.index"))


@bp.route("/dashboard")
def index():
    return render_template("dashboard.html")


@bp.route("/health")
def health():
    return jsonify({"status": "ok"})
