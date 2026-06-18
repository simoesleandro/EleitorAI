from core.modelos import ClaimExtraida, ResultadoVerificacao

_VEREDITO_EMOJI = {
    "verdadeiro": "[V]",
    "falso": "[F]",
    "enganoso": "[E]",
    "impreciso": "[I]",
    "sem_contexto": "[?]",
}


def gerar_dossie_md(conteudo: str, checagens: list[tuple[ClaimExtraida, ResultadoVerificacao]]) -> str:
    linhas = ["# Dossie Veritas", ""]
    linhas.extend([f"**Conteudo analisado:** {conteudo}", ""])
    linhas.extend([f"**Total de checagens:** {len(checagens)}", ""])
    falsos = sum(1 for _, rv in checagens if rv.veredito == "falso")
    linhas.extend([f"**Vereditos falsos:** {falsos}", ""])
    linhas.extend(["---", ""])
    for i, (claim, rv) in enumerate(checagens, 1):
        emoji = _VEREDITO_EMOJI.get(rv.veredito, "[?]")
        linhas.extend([f"### Claim {i}: {emoji} {rv.veredito.upper()}", ""])
        linhas.extend([f"**Afirmacao:** {claim.texto}", ""])
        linhas.extend([f"**Confianca:** {rv.confianca:.0%} (fontes independentes: {rv.fontes_independentes})", ""])
        linhas.extend([f"**Justificativa:** {rv.justificativa}", ""])
        linhas.extend(["**Evidencias:**", ""])
        for ev in rv.evidencias:
            url_part = f" ([fonte]({ev.url}))" if ev.url else ""
            linhas.append(f"- **{ev.fonte}**: {ev.trecho}{url_part}")
        linhas.append("")
        linhas.extend([f"**Contraposicao sugerida:** _{rv.contraposicao_sugerida}_", ""])
        linhas.extend(["---", ""])
    return "\n".join(linhas)
