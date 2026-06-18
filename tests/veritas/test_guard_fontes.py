from veritas.agentes.verificador import validar_guard_fontes
from core.modelos import Evidencia, ResultadoVerificacao


def test_guard_fontes_bloqueia_falso_com_uma_fonte():
    rv = ResultadoVerificacao(
        veredito="falso", evidencias=[Evidencia(fonte="x", trecho="y")],
        fontes_independentes=1, confianca=0.9, justificativa="", contraposicao_sugerida=""
    )
    resultado_validacao = validar_guard_fontes(rv)
    assert resultado_validacao["passou"] is False
    assert "insufficient_evidence" in resultado_validacao["motivo"]


def test_guard_fontes_permite_falso_com_duas_fontes():
    rv = ResultadoVerificacao(
        veredito="falso", evidencias=[
            Evidencia(fonte="a", trecho="x"), Evidencia(fonte="b", trecho="y")
        ],
        fontes_independentes=2, confianca=0.9, justificativa="", contraposicao_sugerida=""
    )
    assert validar_guard_fontes(rv)["passou"] is True


def test_guard_fontes_nao_aplica_para_outros_vereditos():
    rv = ResultadoVerificacao(
        veredito="verdadeiro", evidencias=[Evidencia(fonte="x", trecho="y")],
        fontes_independentes=1, confianca=0.9, justificativa="", contraposicao_sugerida=""
    )
    assert validar_guard_fontes(rv)["passou"] is True
