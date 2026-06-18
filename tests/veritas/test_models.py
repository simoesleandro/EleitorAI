import pytest
from pydantic import ValidationError
from core.modelos import FactCheck, ClaimExtraida, ResultadoVerificacao, Evidencia


def test_fact_check_valid():
    fc = FactCheck(
        titulo="Crescimento populacional zero",
        veiculo="Lupa",
        url="https://lupa.com.br/x",
        data="2026-06-18",
        veredito_original="falso",
        claim_checada="Zero crescimento em 10 anos",
        explicacao="IBGE aponta 8.2%",
        fontes_agencia=["IBGE"],
    )
    assert fc.veiculo == "Lupa"


def test_claim_extraida_checavel_false_para_opiniao():
    c = ClaimExtraida(texto="vou melhorar a saude", checavel=False, confianca=0.9)
    assert c.checavel is False


def test_resultado_verificacao_falso_exige_evidencias():
    r = ResultadoVerificacao(
        veredito="falso",
        evidencias=[Evidencia(fonte="a", trecho="x"), Evidencia(fonte="b", trecho="y")],
        fontes_independentes=2,
        confianca=0.9,
        justificativa="contra IBGE",
        contraposicao_sugerida="cresceu 8.2%",
    )
    assert r.veredito == "falso"


def test_resultado_verificacao_veredito_invalido_raises():
    with pytest.raises(ValidationError):
        ResultadoVerificacao(
            veredito="invalido",
            evidencias=[],
            fontes_independentes=0,
            confianca=0.1,
            justificativa="",
            contraposicao_sugerida="",
        )
