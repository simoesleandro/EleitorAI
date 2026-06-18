import json
import logging
from typing import Any

from core.db import get_db
from core.modelos import Alerta, ClaimExtraida, ResultadoVerificacao
from core.notifier import enviar_alerta
from veritas.pipeline import rodar_veritas, VeritasState
from veritas.seed_base import seed_base_fatos

logger = logging.getLogger(__name__)


def job_veritas_check(payload: dict[str, Any]) -> dict:
    conteudo = payload.get("conteudo", "")
    mencao_id = payload.get("mencao_id")
    state = rodar_veritas(conteudo, mencao_id=mencao_id)
    _salvar_checagens(state, mencao_id)
    _enviar_alertas_se_falso(state)
    return {"status": state["status"], "dossie_md": state.get("dossie_md")}


def job_veritas_seed(payload: dict[str, Any]) -> dict:
    return seed_base_fatos()


def job_veritas_atualiza_base(payload: dict[str, Any]) -> dict:
    return seed_base_fatos()


def _salvar_checagens(state: VeritasState, mencao_id: int | None) -> None:
    conn = get_db()
    try:
        for claim, rv in state.get("checagens", []):
            cursor = conn.execute(
                """INSERT INTO afirmacoes (mencao_id, texto, sujeito, predicado, checavel, confianca_extracao)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (mencao_id, claim.texto, claim.sujeito, claim.predicado,
                 int(claim.checavel), claim.confianca),
            )
            afirmacao_id = cursor.lastrowid
            conn.execute(
                """INSERT INTO checagens
                   (afirmacao_id, veredito, evidencias, fontes_independentes, confianca, justificativa, contraposicao_sugerida, modelo)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (afirmacao_id, rv.veredito,
                 json.dumps([e.model_dump() for e in rv.evidencias], ensure_ascii=False),
                 rv.fontes_independentes, rv.confianca, rv.justificativa,
                 rv.contraposicao_sugerida, "gemini"),
            )
        conn.commit()
    finally:
        conn.close()


def _enviar_alertas_se_falso(state: VeritasState) -> None:
    for claim, rv in state.get("checagens", []):
        if rv.veredito in ("falso", "enganoso"):
            alerta = Alerta(
                modulo="veritas",
                severidade="alto" if rv.veredito == "falso" else "medio",
                titulo=f"Claim {rv.veredito}: {claim.texto[:80]}",
                payload={"veredito": rv.veredito, "contraposicao": rv.contraposicao_sugerida},
            )
            enviar_alerta(alerta)
