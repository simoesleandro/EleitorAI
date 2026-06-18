from veritas.ferramentas.ibge import buscar_ibge, _query_populacao


def test_query_populacao_retorna_dados(respx_mock):
    respx_mock.get("https://servicodados.ibge.gov.br/api/v1/projecoes/populacao").respond(
        200, json={"projecao": {"populacao": 215000000}}
    )
    result = _query_populacao()
    assert "populacao" in str(result)


def test_buscar_ibge_crescimento(respx_mock):
    respx_mock.get("https://servicodados.ibge.gov.br/api/v3/agregados").respond(
        200, json=[{"id": "659", "nome": "Censo Demografico"}]
    )
    results = buscar_ibge("crescimento populacional 2022")
    assert isinstance(results, list)
