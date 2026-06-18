from unittest.mock import patch
from veritas.agentes.extrator import extrair_claims
from core.modelos import ClaimExtraida


def test_extrair_claims_retorna_lista_de_claims_extraida():
    from veritas.agentes.extrator import _ListaClaims
    fake_claims = [
        ClaimExtraida(texto="zero crescimento", checavel=True, confianca=0.95),
        ClaimExtraida(texto="vou melhorar", checavel=False, confianca=0.9),
    ]
    with patch("veritas.agentes.extrator.gerar_resposta", return_value=_ListaClaims(claims=fake_claims)):
        result = extrair_claims("Texto qualquer do discurso")
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(c, ClaimExtraida) for c in result)


def test_extrair_claims_filtrar_nao_checaveis_opicional():
    from veritas.agentes.extrator import _ListaClaims
    fake_claims = [
        ClaimExtraida(texto="x", checavel=True, confianca=0.9),
        ClaimExtraida(texto="y", checavel=False, confianca=0.8),
    ]
    with patch("veritas.agentes.extrator.gerar_resposta", return_value=_ListaClaims(claims=fake_claims)):
        result = extrair_claims("discurso", apenas_checaveis=True)
    assert len(result) == 1
    assert result[0].checavel is True
