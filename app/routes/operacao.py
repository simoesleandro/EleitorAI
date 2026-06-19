from flask import Blueprint, render_template

from core.db import get_db

bp = Blueprint("operacao", __name__, url_prefix="/operacao")


@bp.route("/alertas")
def alertas():
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT id, modulo, severidade, titulo, enviado_telegram, criado_em
               FROM alertas ORDER BY criado_em DESC LIMIT 100"""
        ).fetchall()
        alertas = [dict(r) for r in rows]
    finally:
        conn.close()
    stats = {
        "total": len(alertas),
        "alto": sum(1 for a in alertas if a["severidade"] == "alto"),
        "medio": sum(1 for a in alertas if a["severidade"] == "medio"),
    }
    return render_template("alertas.html", alertas=alertas, stats=stats)
