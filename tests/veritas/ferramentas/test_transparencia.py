from veritas.ferramentas.transparencia import buscar_transparencia, _query_despesas


def test_query_despesas_retorna_dados(respx_mock):
    respx_mock.get("https://api.portaldatransparencia.gov.br/api/despesas/v2").respond(
        200, json=[{"empresa": "Fornecedor X", "valor": 50000}]
    )
    result = _query_despesas("educacao")
    assert isinstance(result, list)
    assert result[0]["empresa"] == "Fornecedor X"


def test_buscar_transparencia_retorna_lista(respx_mock):
    respx_mock.get("https://api.portaldatransparencia.gov.br/api/despesas/v2").respond(
        200, json=[{"empresa": "Fornecedor X", "valor": 50000}]
    )
    results = buscar_transparencia("educacao")
    assert isinstance(results, list)
