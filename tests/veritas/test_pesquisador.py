from unittest.mock import patch
from veritas.agentes.pesquisador import pesquisar_evidencias, TOOL_REGISTRY
from core.modelos import ClaimExtraida, Evidencia


def test_tool_registry_tem_todas_ferramentas():
    esperadas = {"buscar_factcheck", "buscar_ibge", "buscar_tse", "buscar_tesouro",
                 "buscar_datasus", "buscar_transparencia", "buscar_noticias"}
    assert esperadas.issubset(set(TOOL_REGISTRY.keys()))


def test_pesquisar_evidencias_retorna_lista_de_evidencia():
    claim = ClaimExtraida(texto="zero crescimento populacional", checavel=True, confianca=0.95)
    fake_evidencias = [Evidencia(fonte="IBGE", trecho="cresceu 8.2%", url="https://ibge.gov.br")]
    with patch("veritas.agentes.pesquisador._exec_react_loop", return_value=fake_evidencias):
        result = pesquisar_evidencias(claim)
    assert isinstance(result, list)
    assert all(isinstance(e, Evidencia) for e in result)


def test_pesquisar_evidencias_falha_graciosamente():
    claim = ClaimExtraida(texto="x", checavel=True, confianca=0.9)
    with patch("veritas.agentes.pesquisador._exec_react_loop", side_effect=Exception("API fora")):
        result = pesquisar_evidencias(claim)
    assert result == []
