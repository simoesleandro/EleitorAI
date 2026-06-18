from veritas.ferramentas.datasus import buscar_datasus, _query_mortalidade


def test_query_mortalidade_retorna_dados(respx_mock):
    respx_mock.get("http://tabnet.datasus.gov.br/cnv/obt10uf").respond(
        200, json={"linhas": [{"uf": "SP", "obitos": 50000}]}
    )
    result = _query_mortalidade("SP")
    assert "linhas" in result
    assert result["linhas"][0]["uf"] == "SP"


def test_buscar_datasus_retorna_lista(respx_mock):
    respx_mock.get("http://tabnet.datasus.gov.br/cnv/obt10uf").respond(
        200, json={"linhas": [{"uf": "SP", "obitos": 50000}]}
    )
    results = buscar_datasus("SP")
    assert isinstance(results, list)
