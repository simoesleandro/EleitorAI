from pathlib import Path

from core.llm import gerar_resposta
from core.modelos import ClaimExtraida, Evidencia, ResultadoVerificacao

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "verificador.txt"


def verificar_claim(claim: ClaimExtraida, evidencias: list[Evidencia]) -> ResultadoVerificacao:
    prompt_sistema = _PROMPT_PATH.read_text(encoding="utf-8")
    evidencias_str = "\n".join(
        f"- [{e.fonte}] {e.trecho} (url: {e.url or 'n/a'})" for e in evidencias
    )
    prompt = (
        f"{prompt_sistema}\n\n"
        f"Afirmacao: {claim.texto}\n"
        f"Sujeito: {claim.sujeito or 'n/a'}\n"
        f"Predicado: {claim.predicado or 'n/a'}\n\n"
        f"Evidencias coletadas:\n{evidencias_str}\n"
    )
    return gerar_resposta(prompt, response_schema=ResultadoVerificacao)


def validar_guard_fontes(rv: ResultadoVerificacao) -> dict:
    if rv.veredito == "falso" and rv.fontes_independentes < 2:
        return {
            "passou": False,
            "motivo": "insufficient_evidence",
            "detalhe": f"falso requer >=2 fontes independentes, tem {rv.fontes_independentes}",
        }
    return {"passou": True, "motivo": "ok"}
