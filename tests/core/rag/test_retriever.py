from unittest.mock import patch
from core.rag.embeddings import indexar
from core.rag.retriever import buscar


def test_buscar_hybrid_combina_keyword_e_semantico(db):
    with patch("core.rag.embeddings.gerar_embedding", return_value=[0.1] * 768):
        indexar("factcheck", 1, "IBGE confirma crescimento populacional de 8.2%")
        indexar("factcheck", 2, "Censo 2022 revela dados demograficos")
        indexar("factcheck", 3, "Receita completamente diferente sobre impostos")
    with patch("core.rag.embeddings.gerar_embedding", return_value=[0.11] * 768):
        results = buscar("crescimento populacional IBGE", entidade_tipo="factcheck", k=5)
    ids = [r["entidade_id"] for r in results]
    assert 1 in ids
    assert 3 not in ids or ids.index(3) > ids.index(1)


def test_buscar_keyword_match_boosta(db):
    with patch("core.rag.embeddings.gerar_embedding", return_value=[0.5] * 768):
        indexar("factcheck", 10, "IBGE crescimento")
        indexar("factcheck", 11, "IBGE crescimento tambem")
    with patch("core.rag.embeddings.gerar_embedding", return_value=[0.5] * 768):
        results = buscar("IBGE", entidade_tipo="factcheck", k=5)
    assert len(results) >= 1
    assert all("IBGE" in r["conteudo"] for r in results)
