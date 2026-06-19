import pytest
from unittest.mock import patch
from eco.clustering import clusterizar_mencoes
from core.modelos import Cluster


def test_clusterizar_retorna_lista_de_cluster():
    mencoes = [
        {"id": i, "texto": f"candidato X ligado a esquema Y variacao {i}"}
        for i in range(10)
    ] + [
        {"id": 100 + i, "texto": f"texto completamente diferente sobre saude {i}"}
        for i in range(8)
    ]
    base_a = [0.1] * 768
    base_b = [0.9] * 768
    fake_embeddings = [list(base_a) for _ in range(10)] + [list(base_b) for _ in range(8)]
    with patch("eco.clustering.gerar_embedding", side_effect=fake_embeddings):
        clusters = clusterizar_mencoes(mencoes, min_cluster_size=5)
    assert isinstance(clusters, list)
    assert all(isinstance(c, Cluster) for c in clusters)
    assert len(clusters) >= 1


def test_clusterizar_descarta_clusters_pequenos():
    mencoes = [{"id": 1, "texto": "a"}, {"id": 2, "texto": "b"}]
    with patch("eco.clustering.gerar_embedding", return_value=[0.1] * 768):
        clusters = clusterizar_mencoes(mencoes, min_cluster_size=5)
    assert clusters == []
