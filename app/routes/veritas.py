from flask import Blueprint, render_template, request, redirect, url_for, Response, jsonify

from core.db import get_db
from core.fila import enqueue

bp = Blueprint("veritas", __name__, url_prefix="/veritas")


@bp.route("/")
def lista():
    conn = get_db()
    try:
        cursor = conn.execute(
            """SELECT c.id, c.veredito, c.confianca, c.criado_em, a.texto as claim
               FROM checagens c JOIN afirmacoes a ON c.afirmacao_id=a.id
               ORDER BY c.criado_em DESC LIMIT 50"""
        )
        checagens = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
    return render_template("veritas_lista.html", checagens=checagens)


@bp.route("/<int:checagem_id>")
def detalhe(checagem_id):
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT c.*, a.texto as claim, a.mencao_id
               FROM checagens c JOIN afirmacoes a ON c.afirmacao_id=a.id
               WHERE c.id=?""",
            (checagem_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return "nao encontrado", 404
    return render_template("veritas_detalhe.html", checagem=dict(row))


@bp.route("/<int:checagem_id>/pdf")
def pdf(checagem_id):
    from veritas.dossie import gerar_dossie_pdf
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM checagens WHERE id=?", (checagem_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        return "nao encontrado", 404
    md = f"# Checagem #{row['id']}\n\nVeredito: {row['veredito']}\n\n{row['justificativa']}"
    try:
        pdf_bytes = gerar_dossie_pdf(md)
    except NotImplementedError as e:
        return str(e), 501
    return Response(pdf_bytes, mimetype="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=dossie_{checagem_id}.pdf"})


@bp.route("/novo", methods=["POST"])
def novo():
    conteudo = request.form.get("conteudo", "")
    mencao_id = request.form.get("mencao_id")
    payload = {"conteudo": conteudo}
    if mencao_id:
        payload["mencao_id"] = int(mencao_id)
    job_id = enqueue("veritas", "veritas_check", payload)
    return redirect(url_for("veritas.lista"))
