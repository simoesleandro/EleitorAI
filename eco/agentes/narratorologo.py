from pathlib import Path
from typing import Tuple

from pydantic import BaseModel, Field

from core.llm import gerar_resposta
from core.modelos import Cluster

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "narratorologo.txt"


class _ResultadoNomeacao(BaseModel):
    nome: str
    descricao: str
    candidatos_afetados: list[str] = Field(default_factory=list)


def nomear_narrativa(cluster: Cluster, classificacao: str) -> Tuple[str, str, list[str]]:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = (
        f"{prompt_sistema}\n\n"
        f"Cluster: {cluster.centroide_texto}\n"
        f"Volume: {cluster.volume}\n"
        f"Classificacao: {classificacao}\n"
    )
    resultado = gerar_resposta(prompt, response_schema=_ResultadoNomeacao)
    return resultado.nome, resultado.descricao, resultado.candidatos_afetados
