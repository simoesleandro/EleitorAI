from veritas.ferramentas.tse import buscar_tse, _query_candidatos


def test_query_candidatos_retorna_dados(respx_mock):
    respx_mock.get("https://dadosabertos.tse.jus.br/api/v2/candidatos").respond(
        200, json=[{"id": 1, "nome": "Candidato X", "uf": "SP"}]
    )
    result = _query_candidatos("SP")
    assert isinstance(result, list)
    assert result[0]["uf"] == "SP"


def test_buscar_tse_retorna_lista(respx_mock):
    respx_mock.get("https://dadosabertos.tse.jus.br/api/v2/candidatos").respond(
        200, json=[{"id": 1, "nome": "Candidato X", "uf": "SP"}]
    )
    results = buscar_tse("SP")
    assert isinstance(results, list)
