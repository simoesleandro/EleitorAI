from pathlib import Path

from pydantic import BaseModel, Field

from core.llm import gerar_resposta
from core.modelos import ClaimExtraida, ResultadoVerificacao

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "critico.txt"


class RevisaoCritica(BaseModel):
    aprova: bool
    problemas: list[str] = Field(default_factory=list)
    sugestao: str = ""


def revisar_checagem(checagem: ResultadoVerificacao, claim: ClaimExtraida) -> dict:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    evidencias_str = "\n".join(f"- [{e.fonte}] {e.trecho} ({e.url or 'sem url'})" for e in checagem.evidencias)
    prompt = (
        f"{prompt_sistema}\n\n"
        f"Claim: {claim.texto}\n"
        f"Veredito: {checagem.veredito}\n"
        f"Fontes independentes: {checagem.fontes_independentes}\n"
        f"Confianca: {checagem.confianca}\n"
        f"Justificativa: {checagem.justificativa}\n"
        f"Contraposicao: {checagem.contraposicao_sugerida}\n"
        f"Evidencias:\n{evidencias_str}\n"
    )
    revisao = gerar_resposta(prompt, response_schema=RevisaoCritica)
    return revisao.model_dump()
