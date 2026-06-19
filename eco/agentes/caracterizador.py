import json
from pathlib import Path
from typing import Tuple

from pydantic import BaseModel

from core.llm import gerar_resposta
from core.modelos import ClassificacaoNarrativa, Cluster

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "caracterizador.txt"


class _ResultadoCaracterizacao(BaseModel):
    classificacao: ClassificacaoNarrativa
    justificativa: str
    confianca: float


def caracterizar_narrativa(cluster: Cluster, features_rede: dict) -> Tuple[ClassificacaoNarrativa, str, float]:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = (
        f"{prompt_sistema}\n\n"
        f"Cluster: {cluster.centroide_texto}\n"
        f"Volume: {cluster.volume}\n"
        f"Features da rede: {json.dumps(features_rede, default=str)}\n"
    )
    resultado = gerar_resposta(prompt, response_schema=_ResultadoCaracterizacao)
    return resultado.classificacao, resultado.justificativa, resultado.confianca
