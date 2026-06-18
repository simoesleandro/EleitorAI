import json
import logging
import re
from pathlib import Path
from typing import Callable

from core.llm import gerar_resposta
from core.modelos import ClaimExtraida, Evidencia
from veritas.ferramentas.base_fatos import buscar_factcheck
from veritas.ferramentas.ibge import buscar_ibge
from veritas.ferramentas.tse import buscar_tse
from veritas.ferramentas.tesouro import buscar_tesouro
from veritas.ferramentas.datasus import buscar_datasus
from veritas.ferramentas.transparencia import buscar_transparencia
from veritas.ferramentas.noticias import buscar_noticias

logger = logging.getLogger(__name__)
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "pesquisador.txt"

TOOL_REGISTRY: dict[str, Callable] = {
    "buscar_factcheck": buscar_factcheck,
    "buscar_ibge": buscar_ibge,
    "buscar_tse": buscar_tse,
    "buscar_tesouro": buscar_tesouro,
    "buscar_datasus": buscar_datasus,
    "buscar_transparencia": buscar_transparencia,
    "buscar_noticias": buscar_noticias,
}

MAX_ITERACOES = 6


def pesquisar_evidencias(claim: ClaimExtraida) -> list[Evidencia]:
    try:
        return _exec_react_loop(claim)
    except Exception as e:
        logger.error(f"pesquisador falhou para claim '{claim.texto}': {e}")
        return []


def _exec_react_loop(claim: ClaimExtraida) -> list[Evidencia]:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    tools_desc = "\n".join(f"- {name}" for name in TOOL_REGISTRY.keys())
    history = f"{prompt_sistema}\n\nTools disponiveis:\n{tools_desc}\n\n"
    history += f"Claim a checar: {claim.texto}\n\n"

    evidencias: list[Evidencia] = []
    for i in range(MAX_ITERACOES):
        resposta = gerar_resposta(history)
        if "Final Answer:" in resposta:
            return _parse_final_answer(resposta, evidencias)
        action_match = re.search(r"Action:\s*(\w+)\s*\nAction Input:\s*(.+?)(?:\n|$)", resposta, re.DOTALL)
        if not action_match:
            break
        tool_name = action_match.group(1).strip()
        tool_input = action_match.group(2).strip()
        tool = TOOL_REGISTRY.get(tool_name)
        if not tool:
            history += f"Observation: tool '{tool_name}' nao existe. Use: {list(TOOL_REGISTRY.keys())}\n\n"
            continue
        try:
            result = tool(tool_input)
            history += f"Observation: {json.dumps(result, ensure_ascii=False, default=str)[:2000]}\n\n"
            for r in result if isinstance(result, list) else []:
                if isinstance(r, dict) and "fonte" in r:
                    evidencias.append(Evidencia(
                        fonte=r["fonte"],
                        trecho=str(r.get("dados", r.get("conteudo", "")))[:500],
                        url=r.get("url"),
                    ))
        except Exception as e:
            history += f"Observation: erro: {e}\n\n"
    return evidencias


def _parse_final_answer(resposta: str, evidencias_coletadas: list[Evidencia]) -> list[Evidencia]:
    final_part = resposta.split("Final Answer:")[-1]
    if "nenhuma evidencia" in final_part.lower():
        return []
    return evidencias_coletadas
