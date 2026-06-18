from pathlib import Path

from pydantic import BaseModel

from core.llm import gerar_resposta
from core.modelos import ClaimExtraida

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extrator.txt"


class _ListaClaims(BaseModel):
    claims: list[ClaimExtraida]


def extrair_claims(texto: str, apenas_checaveis: bool = False) -> list[ClaimExtraida]:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = f"{prompt_sistema}\n\nTexto para analisar:\n{texto}"
    resposta = gerar_resposta(prompt, response_schema=_ListaClaims)
    claims = resposta.claims
    if apenas_checaveis:
        claims = [c for c in claims if c.checavel]
    return claims
