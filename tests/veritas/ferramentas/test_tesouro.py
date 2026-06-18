from veritas.ferramentas.tesouro import buscar_tesouro, _query_receitas


def test_query_receitas_retorna_dados(respx_mock):
    respx_mock.get("https://apidatalake.tesouro.gov.br/ords/siconfi/v2/ente/3550308/receitas").respond(
        200, json={"items": [{"conta": "Receita Tributaria", "valor": 1000000}]}
    )
    result = _query_receitas("3550308")
    assert "items" in result
    assert result["items"][0]["valor"] == 1000000


def test_buscar_tesouro_retorna_lista(respx_mock):
    respx_mock.get("https://apidatalake.tesouro.gov.br/ords/siconfi/v2/ente/3550308/receitas").respond(
        200, json={"items": [{"conta": "Receita Tributaria", "valor": 1000000}]}
    )
    results = buscar_tesouro("3550308")
    assert isinstance(results, list)
