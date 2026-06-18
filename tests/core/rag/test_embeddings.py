from unittest.mock import patch
from core.rag.embeddings import indexar, buscar_similares, remover


def test_indexar_insere_embedding(db):
    fake_embedding = [0.1] * 768
    with patch("core.rag.embeddings.gerar_embedding", return_value=fake_embedding):
        indexar("factcheck", 1, "IBGE confirma crescimento 8.2%")
    with patch("core.rag.embeddings.gerar_embedding", return_value=[0.11] * 768):
        results = buscar_similares("crescimento populacional", k=1)
    assert len(results) == 1
    assert results[0]["entidade_tipo"] == "factcheck"
    assert results[0]["entidade_id"] == 1


def test_buscar_filtra_por_tipo(db):
    fake = [0.1] * 768
    with patch("core.rag.embeddings.gerar_embedding", return_value=fake):
        indexar("factcheck", 1, "AAA")
        indexar("mencao", 1, "BBB")
    with patch("core.rag.embeddings.gerar_embedding", return_value=fake):
        results = buscar_similares("query", entidade_tipo="factcheck", k=5)
    assert all(r["entidade_tipo"] == "factcheck" for r in results)


def test_remover(db):
    with patch("core.rag.embeddings.gerar_embedding", return_value=[0.1] * 768):
        indexar("factcheck", 99, "para remover")
        remover("factcheck", 99)
        results = buscar_similares("para remover", entidade_tipo="factcheck", k=10)
    assert all(r["entidade_id"] != 99 for r in results)
