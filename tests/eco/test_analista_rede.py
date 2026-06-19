import pytest
import networkx as nx
from eco.agentes.analista_rede import analisar_rede
from core.modelos import Amplificador


def test_analisar_rede_retora_features():
    grafo = nx.DiGraph()
    grafo.add_edge("origem", "a", tipo="forward")
    grafo.add_edge("origem", "b", tipo="forward")
    grafo.add_edge("origem", "c", tipo="forward")
    metricas = {"degree": dict(grafo.degree()), "in_degree": dict(grafo.in_degree()),
                "betweenness": {}, "comunidades": []}
    amplificadores = [Amplificador(identificador="origem", tipo="telegram_channel", centralidade=1.0)]
    features = analisar_rede(grafo, metricas, amplificadores)
    assert "num_contas" in features
    assert "max_degree" in features
    assert features["num_contas"] == 4
    assert features["max_degree"] == 3
