from eco.grafo import construir_grafo, calcular_metricas, extrair_amplificadores
from core.modelos import Amplificador


def test_construir_grafo_telegram_forwards():
    mencoes = [
        {"id": 1, "autor_id": "100", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:00:00"},
        {"id": 2, "autor_id": "101", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:05:00"},
        {"id": 3, "autor_id": "102", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:10:00"},
        {"id": 4, "autor_id": "200", "texto": "x", "metricas": {}, "timestamp": "2026-06-18T09:55:00"},
    ]
    grafo = construir_grafo(mencoes)
    assert "200" in grafo.nodes()
    assert "100" in grafo.nodes()
    assert grafo.has_edge("200", "100") or grafo.has_edge("100", "200")


def test_calcular_metricas_retorna_degree():
    mencoes = [
        {"id": 1, "autor_id": "100", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:00:00"},
        {"id": 2, "autor_id": "101", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:05:00"},
    ]
    grafo = construir_grafo(mencoes)
    metricas = calcular_metricas(grafo)
    assert "degree" in metricas
    assert "200" in metricas["degree"]


def test_extrair_amplificadores_retorna_lista():
    mencoes = [
        {"id": 1, "autor_id": "100", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:00:00"},
        {"id": 2, "autor_id": "101", "texto": "x", "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:05:00"},
    ]
    grafo = construir_grafo(mencoes)
    metricas = calcular_metricas(grafo)
    amplifs = extrair_amplificadores(grafo, metricas, tipo="telegram_channel")
    assert isinstance(amplifs, list)
    assert all(isinstance(a, Amplificador) for a in amplifs)
    ids = [a.identificador for a in amplifs]
    assert "200" in ids
