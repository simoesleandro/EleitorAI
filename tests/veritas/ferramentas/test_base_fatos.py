from unittest.mock import patch
from veritas.ferramentas.base_fatos import buscar_factcheck


def test_buscar_factcheck_delega_para_retriever_com_filtro():
    fake_results = [{"entidade_tipo": "factcheck", "entidade_id": 1, "conteudo": "x", "score_total": 0.9}]
    with patch("veritas.ferramentas.base_fatos.buscar", return_value=fake_results) as mock_buscar:
        result = buscar_factcheck("crescimento populacional")
    assert result == fake_results
    mock_buscar.assert_called_once_with("crescimento populacional", entidade_tipo="factcheck", k=5)
