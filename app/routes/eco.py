from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from core.db import get_db
from core.fila import enqueue

bp = Blueprint("eco", __name__, url_prefix="/eco")


@bp.route("/")
def lista():
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT id, cluster_id, nome, descricao, volume, classificacao,
                      confianca_classificacao, criado_em
               FROM narrativas ORDER BY criado_em DESC LIMIT 50"""
        ).fetchall()
        narrativas = [dict(r) for r in rows]
        stats = {
            "total": len(narrativas),
            "coordenado": sum(1 for n in narrativas if n["classificacao"] == "coordenado"),
            "suspeito_bot": sum(1 for n in narrativas if n["classificacao"] == "suspeito_bot"),
            "amplificado": sum(1 for n in narrativas if n["classificacao"] == "amplificado"),
            "organico": sum(1 for n in narrativas if n["classificacao"] == "organico"),
        }
        recent_jobs = [dict(r) for r in conn.execute(
            """SELECT id, tipo, status, criado_em, concluido_em
               FROM job_queue
               WHERE modulo = 'eco'
               ORDER BY id DESC LIMIT 5"""
        ).fetchall()]
    finally:
        conn.close()
    return render_template(
        "eco_lista.html",
        narrativas=narrativas,
        stats=stats,
        recent_jobs=recent_jobs,
    )


@bp.route("/<int:narrativa_id>")
def detalhe(narrativa_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM narrativas WHERE id=?", (narrativa_id,),
        ).fetchone()
        if not row:
            abort(404)
        narrativa = dict(row)
        amplificadores = [dict(r) for r in conn.execute(
            "SELECT * FROM amplificadores WHERE narrativa_id=? ORDER BY centralidade DESC",
            (narrativa_id,),
        ).fetchall()]
        relacoes = [dict(r) for r in conn.execute(
            "SELECT * FROM relacoes_amplificacao WHERE narrativa_id=? LIMIT 200",
            (narrativa_id,),
        ).fetchall()]
    finally:
        conn.close()
    return render_template(
        "eco_detalhe.html",
        narrativa=narrativa,
        amplificadores=amplificadores,
        relacoes=relacoes,
    )


@bp.route("/<int:narrativa_id>/grafo")
def grafo(narrativa_id):
    conn = get_db()
    try:
        narrativa = conn.execute(
            "SELECT id, cluster_id, nome, classificacao FROM narrativas WHERE id=?",
            (narrativa_id,),
        ).fetchone()
        if not narrativa:
            abort(404)
        amplificadores = [dict(r) for r in conn.execute(
            "SELECT identificador, tipo, centralidade, suspeita_bot FROM amplificadores WHERE narrativa_id=?",
            (narrativa_id,),
        ).fetchall()]
        relacoes = [dict(r) for r in conn.execute(
            "SELECT de_identificador, para_identificador, peso, tipo FROM relacoes_amplificacao WHERE narrativa_id=?",
            (narrativa_id,),
        ).fetchall()]
    finally:
        conn.close()
    nodes = [{"id": a["identificador"], "tipo": a["tipo"],
              "centralidade": a["centralidade"], "suspeita_bot": bool(a["suspeita_bot"])}
             for a in amplificadores]
    links = [{"source": r["de_identificador"], "target": r["para_identificador"],
              "peso": r["peso"], "tipo": r["tipo"]} for r in relacoes]
    return render_template(
        "eco_grafo.html",
        narrativa=dict(narrativa),
        nodes_json=jsonify({"nodes": nodes, "links": links}).get_json(),
    )


@bp.route("/analyze", methods=["POST"])
def trigger_analyze():
    try:
        janela = int(request.form.get("janela_horas", 24))
    except (TypeError, ValueError):
        janela = 24
    janela = max(1, min(janela, 168))
    job_id = enqueue("eco", "eco_analyze", {"janela_horas": janela})
    flash(f"Análise Eco agendada. Job #{job_id} (janela {janela}h). O worker processa em até 60s. Recarregue esta página.", "success")
    return redirect(url_for("eco.lista"))


@bp.route("/coleta", methods=["POST"])
def trigger_coleta():
    handle = (request.form.get("instagram_handle") or "").strip()
    try:
        limite = int(request.form.get("limite", 20))
    except (TypeError, ValueError):
        limite = 20
    limite = max(1, min(limite, 100))
    payload = {"limite": limite}
    if handle:
        payload["instagram_handle"] = handle
    job_id = enqueue("eco", "eco_coleta", payload)
    if handle:
        flash(f"Coleta Instagram agendada para {handle} (limite {limite}). Job #{job_id}.", "success")
    else:
        flash(f"Coleta de fontes configuradas agendada. Job #{job_id}.", "info")
    return redirect(url_for("eco.lista"))
