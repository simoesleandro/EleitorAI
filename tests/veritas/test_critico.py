from unittest.mock import patch
from veritas.agentes.critico import revisar_checagem, RevisaoCritica
from core.modelos import ClaimExtraida, Evidencia, ResultadoVerificacao


def test_revisar_checagem_aprova_boa_checagem():
    rv = ResultadoVerificacao(
        veredito="falso",
        evidencias=[Evidencia(fonte="IBGE", trecho="8.2%", url="https://ibge.gov.br/censo"),
                    Evidencia(fonte="Lupa", trecho="checagem anterior", url="https://lupa.com.br/x")],
        fontes_independentes=2, confianca=0.9,
        justificativa="IBGE aponta 8.2% no Censo 2022, Lupa ja havia checado como falso",
        contraposicao_sugerida="Candidato X mente sobre dados do IBGE. Crescemos 8.2% segundo Censo 2022."
    )
    claim = ClaimExtraida(texto="zero crescimento", checavel=True, confianca=0.9)
    fake_review = RevisaoCritica(aprova=True, problemas=[], sugestao="")
    with patch("veritas.agentes.critico.gerar_resposta", return_value=fake_review):
        result = revisar_checagem(rv, claim)
    assert result["aprova"] is True


def test_revisar_checagem_rejeita_sem_evidencia():
    rv = ResultadoVerificacao(
        veredito="falso",
        evidencias=[Evidencia(fonte="x", trecho="y", url=None)],
        fontes_independentes=1, confianca=0.5,
        justificativa="",
        contraposicao_sugerida="x"
    )
    fake_review = RevisaoCritica(aprova=False, problemas=["sem fontes rastreaveis", "contraposicao agressiva"], sugestao="adicionar mais fontes")
    with patch("veritas.agentes.critico.gerar_resposta", return_value=fake_review):
        result = revisar_checagem(rv, ClaimExtraida(texto="x", checavel=True, confianca=0.9))
    assert result["aprova"] is False
    assert len(result["problemas"]) > 0
