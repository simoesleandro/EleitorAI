from unittest.mock import patch
from veritas.pipeline import rodar_veritas
from core.modelos import ClaimExtraida, Evidencia, ResultadoVerificacao


def test_rodar_veritas_pipeline_completo_com_mock():
    conteudo = "Candidato afirmou zero crescimento populacional."
    fake_claims = [ClaimExtraida(texto="zero crescimento", checavel=True, confianca=0.95)]
    fake_evidencias = [Evidencia(fonte="IBGE", trecho="8.2%", url="u"),
                       Evidencia(fonte="Lupa", trecho="falso", url="u2")]
    fake_resultado = ResultadoVerificacao(
        veredito="falso", evidencias=fake_evidencias, fontes_independentes=2,
        confianca=0.9, justificativa="IBGE 8.2%", contraposicao_sugerida="cresceu 8.2%"
    )
    fake_review = {"aprova": True, "problemas": [], "sugestao": ""}

    with patch("veritas.pipeline.extrair_claims", return_value=fake_claims), \
         patch("veritas.pipeline.pesquisar_evidencias", return_value=fake_evidencias), \
         patch("veritas.pipeline.verificar_claim", return_value=fake_resultado), \
         patch("veritas.pipeline.revisar_checagem", return_value=fake_review):
        state = rodar_veritas(conteudo)
    assert state["status"] == "concluido"
    assert state["dossie_md"] is not None
    assert "zero crescimento" in state["dossie_md"]
    assert len(state["checagens"]) == 1


def test_rodar_veritas_guard_falso_com_poucas_fontes_repete_pesquisador():
    conteudo = "x"
    fake_claims = [ClaimExtraida(texto="x", checavel=True, confianca=0.9)]
    fake_evidencias_1 = [Evidencia(fonte="IBGE", trecho="x", url="u")]
    fake_evidencias_2 = [Evidencia(fonte="IBGE", trecho="x", url="u"),
                          Evidencia(fonte="Lupa", trecho="y", url="u2")]
    fake_resultado_1 = ResultadoVerificacao(
        veredito="falso", evidencias=fake_evidencias_1, fontes_independentes=1,
        confianca=0.5, justificativa="", contraposicao_sugerida=""
    )
    fake_resultado_2 = ResultadoVerificacao(
        veredito="falso", evidencias=fake_evidencias_2, fontes_independentes=2,
        confianca=0.9, justificativa="", contraposicao_sugerida=""
    )
    fake_review = {"aprova": True, "problemas": [], "sugestao": ""}

    with patch("veritas.pipeline.extrair_claims", return_value=fake_claims), \
         patch("veritas.pipeline.pesquisar_evidencias", side_effect=[fake_evidencias_1, fake_evidencias_2]), \
         patch("veritas.pipeline.verificar_claim", side_effect=[fake_resultado_1, fake_resultado_2]), \
         patch("veritas.pipeline.revisar_checagem", return_value=fake_review):
        state = rodar_veritas(conteudo)
    assert state["status"] == "concluido"
    assert state["checagens"][0][1].fontes_independentes == 2


def test_rodar_veritas_critico_rejeita_3_vezes_marca_revisar():
    conteudo = "x"
    fake_claims = [ClaimExtraida(texto="x", checavel=True, confianca=0.9)]
    fake_evidencias = [Evidencia(fonte="a", trecho="x", url="u"),
                       Evidencia(fonte="b", trecho="y", url="u2")]
    fake_resultado = ResultadoVerificacao(
        veredito="falso", evidencias=fake_evidencias, fontes_independentes=2,
        confianca=0.9, justificativa="j", contraposicao_sugerida="r"
    )
    fake_review_rejeita = {"aprova": False, "problemas": ["x"], "sugestao": "y"}

    with patch("veritas.pipeline.extrair_claims", return_value=fake_claims), \
         patch("veritas.pipeline.pesquisar_evidencias", return_value=fake_evidencias), \
         patch("veritas.pipeline.verificar_claim", return_value=fake_resultado), \
         patch("veritas.pipeline.revisar_checagem", return_value=fake_review_rejeita):
        state = rodar_veritas(conteudo)
    assert state["status"] == "revisar"
