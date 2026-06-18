from veritas.agentes.redator import gerar_dossie_md
from core.modelos import ClaimExtraida, Evidencia, ResultadoVerificacao


def test_gerar_dossie_md_estrutura_basica():
    claim = ClaimExtraida(texto="zero crescimento", checavel=True, confianca=0.9)
    rv = ResultadoVerificacao(
        veredito="falso",
        evidencias=[Evidencia(fonte="IBGE", trecho="8.2%", url="u")],
        fontes_independentes=2, confianca=0.9,
        justificativa="IBGE aponta 8.2%",
        contraposicao_sugerida="cresceu 8.2%",
    )
    md = gerar_dossie_md("Entrevista do candidato X em 18/jun", [(claim, rv)])
    assert "# Dossie Veritas" in md
    assert "zero crescimento" in md
    assert "FALSO" in md.upper()
    assert "IBGE" in md
    assert "cresceu 8.2%" in md


def test_gerar_dossie_md_multiplas_checagens():
    claims = [
        (ClaimExtraida(texto="c1", checavel=True, confianca=0.9),
         ResultadoVerificacao(veredito="falso", evidencias=[Evidencia(fonte="a", trecho="x")]*2,
                              fontes_independentes=2, confianca=0.9, justificativa="j1", contraposicao_sugerida="r1")),
        (ClaimExtraida(texto="c2", checavel=True, confianca=0.9),
         ResultadoVerificacao(veredito="verdadeiro", evidencias=[Evidencia(fonte="b", trecho="y")],
                              fontes_independentes=1, confianca=0.9, justificativa="j2", contraposicao_sugerida="r2")),
    ]
    md = gerar_dossie_md("ctx", claims)
    assert md.count("### Claim") >= 2
