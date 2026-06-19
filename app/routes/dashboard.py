from flask import Blueprint, render_template

from core.db import get_db

bp = Blueprint("dashboard", __name__)


def _get_kpis() -> dict:
    conn = get_db()
    try:
        mencoes = conn.execute("SELECT COUNT(*) AS c FROM mencoes").fetchone()["c"]
        fontes = conn.execute("SELECT COUNT(*) AS c FROM fontes WHERE ativa = 1").fetchone()["c"]
        checagens = conn.execute("SELECT COUNT(*) AS c FROM checagens").fetchone()["c"]
        falsos = conn.execute("SELECT COUNT(*) AS c FROM checagens WHERE veredito = 'falso'").fetchone()["c"]
        verdadeiros = conn.execute("SELECT COUNT(*) AS c FROM checagens WHERE veredito = 'verdadeiro'").fetchone()["c"]
        enganosos = conn.execute("SELECT COUNT(*) AS c FROM checagens WHERE veredito = 'enganoso'").fetchone()["c"]
        alertas = conn.execute("SELECT COUNT(*) AS c FROM alertas WHERE enviado_telegram = 1").fetchone()["c"]
        queue_pending = conn.execute("SELECT COUNT(*) AS c FROM job_queue WHERE status = 'pending'").fetchone()["c"]
        queue_done = conn.execute("SELECT COUNT(*) AS c FROM job_queue WHERE status = 'done'").fetchone()["c"]
        factchecks_rag = conn.execute("SELECT COUNT(*) AS c FROM embeddings WHERE entidade_tipo = 'factcheck'").fetchone()["c"]
        briefings = conn.execute("SELECT COUNT(*) AS c FROM briefings").fetchone()["c"]
        scheduler_runs = conn.execute("SELECT COUNT(*) AS c FROM scheduler_log").fetchone()["c"]
        last_job_row = conn.execute(
            "SELECT executado_em, job FROM scheduler_log ORDER BY executado_em DESC LIMIT 1"
        ).fetchone()
        last_job = f"{last_job_row['job']} · {last_job_row['executado_em']}" if last_job_row else None
    finally:
        conn.close()
    return {
        "mencoes": mencoes,
        "fontes": fontes,
        "checagens": checagens,
        "falsos": falsos,
        "verdadeiros": verdadeiros,
        "enganosos": enganosos,
        "veritas_falsos": falsos,
        "alertas": alertas,
        "queue_pending": queue_pending,
        "queue_done": queue_done,
        "factchecks_rag": factchecks_rag,
        "briefings": briefings,
        "scheduler_runs": scheduler_runs,
        "last_job": last_job,
    }


@bp.route("/")
def root():
    from flask import redirect, url_for
    return redirect(url_for("dashboard.index"))


@bp.route("/dashboard")
def index():
    kpi = _get_kpis()
    conn = get_db()
    try:
        recent_rows = conn.execute(
            """SELECT c.id, c.veredito, c.confianca, c.criado_em, a.texto AS claim
               FROM checagens c
               LEFT JOIN afirmacoes a ON c.afirmacao_id = a.id
               ORDER BY c.criado_em DESC LIMIT 5"""
        ).fetchall()
        recent = [dict(r) for r in recent_rows]
    finally:
        conn.close()
    return render_template("dashboard.html", kpi=kpi, recent=recent)


@bp.route("/health")
def health():
    from flask import jsonify
    return jsonify({"status": "ok"})
