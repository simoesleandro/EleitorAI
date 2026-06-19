import json
import logging
from typing import Any

from core.db import get_db
from core.modelos import Alerta
from core.notifier import enviar_alerta
from eco.pipeline import rodar_eco

logger = logging.getLogger(__name__)


def job_eco_coleta(payload: dict[str, Any]) -> dict:
    handle = payload.get("instagram_handle")
    if handle:
        try:
            from core.coletores.instagram import coletar_posts
            mencoes = coletar_posts(handle, limite=payload.get("limite", 20))
            _salvar_mencoes_eco(mencoes)
        except Exception as e:
            logger.warning(f"eco coleta instagram falhou: {e}")
    return {"coletado": True}


def job_eco_analyze(payload: dict[str, Any]) -> dict:
    janela = payload.get("janela_horas", 6)
    state = rodar_eco(janela_horas=janela)
    salvos = _salvar_narrativas(state)
    _enviar_alertas_se_coordenado(state)
    return {
        "status": state.get("status"),
        "narrativas_processadas": salvos,
        "janela_horas": janela,
    }


def _salvar_mencoes_eco(mencoes: list) -> int:
    conn = get_db()
    try:
        salvos = 0
        for m in mencoes:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO mencoes
                       (fonte_id, texto, autor, autor_id, timestamp, url, metricas, hash_conteudo)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (m.fonte_id, m.texto, m.autor, m.autor_id, m.timestamp, m.url,
                     json.dumps(m.metricas, default=str), m.hash_conteudo),
                )
                salvos += 1
            except Exception as e:
                logger.warning(f"erro salvando mencao: {e}")
        conn.commit()
        return salvos
    finally:
        conn.close()


def _salvar_narrativas(state: dict) -> int:
    salvos = 0
    for n in state.get("narrativas", []):
        narrativa_id = _upsert_narrativa(n)
        if narrativa_id is not None:
            _salvar_amplificadores(state, narrativa_id, n.cluster_id)
            _salvar_relacoes(state, narrativa_id, n.cluster_id)
            salvos += 1
    return salvos


def _upsert_narrativa(n) -> int | None:
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id FROM narrativas WHERE cluster_id=?",
            (n.cluster_id,),
        ).fetchone()
        if row:
            return row["id"]
        cursor = conn.execute(
            """INSERT INTO narrativas
               (cluster_id, nome, descricao, volume, velocidade_crescimento,
                classificacao, confianca_classificacao, justificativa_classificacao,
                primeiro_post_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (n.cluster_id, n.nome, n.descricao, n.volume, n.velocidade_crescimento,
             n.classificacao, n.confianca, n.justificativa, n.primeiro_post_em),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"erro salvando narrativa: {e}")
        return None
    finally:
        conn.close()


def _salvar_amplificadores(state: dict, narrativa_id: int, cluster_id: str) -> None:
    amplifs = state.get("_amplificadores", {}).get(cluster_id, [])
    if not amplifs:
        return
    conn = get_db()
    try:
        for a in amplifs:
            conn.execute(
                """INSERT INTO amplificadores
                   (narrativa_id, identificador, tipo, centralidade, suspeita_bot, idade_conta_dias)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (narrativa_id, a.identificador, a.tipo, a.centralidade,
                 int(a.suspeita_bot), a.idade_conta_dias),
            )
        conn.commit()
    finally:
        conn.close()


def _salvar_relacoes(state: dict, narrativa_id: int, cluster_id: str) -> None:
    grafo = state.get("_grafos", {}).get(cluster_id)
    if not grafo:
        return
    from eco.grafo import extrair_relacoes
    rels = extrair_relacoes(grafo)
    if not rels:
        return
    conn = get_db()
    try:
        for r in rels:
            conn.execute(
                """INSERT INTO relacoes_amplificacao
                   (narrativa_id, de_identificador, para_identificador, peso, janela_minutos, tipo)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (narrativa_id, r.de_identificador, r.para_identificador,
                 r.peso, r.janela_minutos, r.tipo),
            )
        conn.commit()
    finally:
        conn.close()


def _enviar_alertas_se_coordenado(state: dict) -> None:
    for n in state.get("narrativas", []):
        if n.classificacao in ("coordenado", "suspeito_bot"):
            alerta = Alerta(
                modulo="eco",
                severidade="alto" if n.classificacao == "coordenado" else "critico",
                titulo=f"Narrativa {n.classificacao}: {n.nome}",
                payload={
                    "narrativa_id": n.cluster_id,
                    "volume": n.volume,
                    "confianca": n.confianca,
                },
            )
            enviar_alerta(alerta)
