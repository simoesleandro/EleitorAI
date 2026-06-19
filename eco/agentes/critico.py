from pathlib import Path

from pydantic import BaseModel, Field

from core.llm import gerar_resposta
from core.modelos import Narrativa

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "critico.txt"


class RevisaoCritica(BaseModel):
    aprova: bool
    problemas: list[str] = Field(default_factory=list)
    sugestao: str = ""


def revisar_classificacao(narrativa: Narrativa) -> dict:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = (
        f"{prompt_sistema}\n\n"
        f"Nome: {narrativa.nome}\n"
        f"Descricao: {narrativa.descricao}\n"
        f"Classificacao: {narrativa.classificacao}\n"
        f"Volume: {narrativa.volume}\n"
        f"Confianca: {narrativa.confianca}\n"
        f"Justificativa: {narrativa.justificativa}\n"
        f"Candidatos afetados: {narrativa.candidatos_afetados}\n"
    )
    revisao = gerar_resposta(prompt, response_schema=RevisaoCritica)
    return revisao.model_dump()
