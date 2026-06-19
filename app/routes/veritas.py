from flask import Blueprint, render_template, request, redirect, url_for, Response, jsonify, abort, session, current_app

from core.db import get_db
from core.fila import enqueue

bp = Blueprint("veritas", __name__, url_prefix="/veritas")


def _get_stats() -> dict:
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM checagens").fetchone()["c"]
        falsos = conn.execute("SELECT COUNT(*) AS c FROM checagens WHERE veredito = 'falso'").fetchone()["c"]
        verdadeiros = conn.execute("SELECT COUNT(*) AS c FROM checagens WHERE veredito = 'verdadeiro'").fetchone()["c"]
        enganosos = conn.execute("SELECT COUNT(*) AS c FROM checagens WHERE veredito = 'enganoso'").fetchone()["c"]
    finally:
        conn.close()
    return {"total": total, "falsos": falsos, "verdadeiros": verdadeiros, "enganosos": enganosos}


def _render_dossie_md(checagem_id: int) -> str:
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT c.*, a.texto AS claim
               FROM checagens c
               LEFT JOIN afirmacoes a ON c.afirmacao_id = a.id
               WHERE c.id = ?""",
            (checagem_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return ""
    md = f"# Checagem #{row['id']}\n\n"
    md += f"**Veredito:** {row['veredito']}  \n"
    md += f"**Confianca:** {int(row['confianca']*100)}%  \n"
    md += f"**Fontes independentes:** {row['fontes_independentes']}  \n\n"
    if row["claim"]:
        md += f"## Claim\n\n{row['claim']}\n\n"
    md += f"## Justificativa\n\n{row['justificativa']}\n\n"
    md += f"## Contraposicao sugerida\n\n{row['contraposicao_sugerida']}\n"
    return md


@bp.route("/")
def lista():
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT c.id, c.veredito, c.confianca, c.criado_em, a.texto AS claim
               FROM checagens c
               LEFT JOIN afirmacoes a ON c.afirmacao_id = a.id
               ORDER BY c.criado_em DESC LIMIT 50"""
        ).fetchall()
        checagens = [dict(r) for r in rows]
    finally:
        conn.close()
    return render_template("veritas_lista.html", checagens=checagens, stats=_get_stats())


@bp.route("/novo", methods=["GET"])
def novo_form():
    if current_app.config.get("WTF_CSRF_ENABLED", True):
        from flask_wtf.csrf import generate_csrf
        session["csrf_token"] = generate_csrf()
    return render_template("veritas_novo.html")


@bp.route("/<int:checagem_id>")
def detalhe(checagem_id):
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT c.*, a.texto AS claim, a.mencao_id
               FROM checagens c
               LEFT JOIN afirmacoes a ON c.afirmacao_id = a.id
               WHERE c.id = ?""",
            (checagem_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        abort(404)
    ch = dict(row)
    if ch.get("evidencias"):
        import json
        try:
            ch["evidencias_list"] = json.loads(ch["evidencias"])
        except Exception:
            ch["evidencias_list"] = []
    else:
        ch["evidencias_list"] = []
    return render_template("veritas_detalhe.html", checagem=ch)


@bp.route("/<int:checagem_id>/pdf")
def pdf(checagem_id):
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT c.id, c.veredito FROM checagens c WHERE c.id = ?""",
            (checagem_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        abort(404)

    md = _render_dossie_md(checagem_id)
    try:
        from veritas.dossie import gerar_dossie_pdf
        pdf_bytes = gerar_dossie_pdf(md)
        return Response(pdf_bytes, mimetype="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename=dossie_{checagem_id}.pdf"})
    except NotImplementedError:
        return Response(
            md,
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=dossie_{checagem_id}.md"},
        )
    except Exception as e:
        return render_template(
            "error.html",
            code=500,
            title="Erro ao gerar PDF",
            message="Falha inesperada ao renderizar o dossiê.",
            explanation=f"Detalhe técnico: <code>{e}</code><br>O PDF depende de WeasyPrint (requer GTK). Estamos em ambiente de desenvolvimento Windows - em produção Linux (Fly.io) o PDF funcionará normalmente.",
        ), 500


@bp.route("/<int:checagem_id>/md")
def md_download(checagem_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM checagens WHERE id = ?", (checagem_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        abort(404)
    md = _render_dossie_md(checagem_id)
    return Response(
        md,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=dossie_{checagem_id}.md"},
    )


@bp.route("/novo", methods=["POST"])
def novo():
    conteudo = request.form.get("conteudo", "").strip()
    if not conteudo:
        return redirect(url_for("veritas.novo_form"))
    mencao_id_raw = request.form.get("mencao_id")
    payload = {"conteudo": conteudo}
    if mencao_id_raw:
        try:
            payload["mencao_id"] = int(mencao_id_raw)
        except (TypeError, ValueError):
            pass
    enqueue("veritas", "veritas_check", payload)
    return redirect(url_for("veritas.lista"))
