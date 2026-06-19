import pytest
from unittest.mock import patch
from eco.pipeline import rodar_eco, EcoState
from core.modelos import Cluster, Narrativa


def test_rodar_eco_pipeline_completo(db):
    fake_mencoes = [{"id": i, "texto": f"narrativa x {i}", "autor_id": str(100+i),
                     "metricas": {"forwarded_from": "200"}, "timestamp": "2026-06-18T10:00:00"}
                    for i in range(20)]
    fake_clusters = [Cluster(id="c1", mencao_ids=[i for i in range(20)],
                              centroide_texto="narrativa x", volume=20)]
    fake_features = {"num_contas": 20, "max_degree": 18, "densidade": 0.8,
                     "suspeitos_bot": 0, "contas_jovens": 5}
    fake_classificacao = ("coordenado", "8 contas em 12min", 0.85)
    fake_nome = ("candidato X ligado a Y", "narrativa de corrupcao", ["X"])
    fake_review = {"aprova": True, "problemas": []}

    with patch("eco.pipeline._query_mencoes_janela", return_value=fake_mencoes), \
         patch("eco.pipeline.clusterizar_mencoes", return_value=fake_clusters), \
         patch("eco.pipeline._detectar_emergentes", return_value=fake_clusters), \
         patch("eco.pipeline.construir_grafo", return_value=None), \
         patch("eco.pipeline.calcular_metricas", return_value={}), \
         patch("eco.pipeline.extrair_amplificadores", return_value=[]), \
         patch("eco.pipeline.analisar_rede", return_value=fake_features), \
         patch("eco.pipeline.caracterizar_narrativa", return_value=fake_classificacao), \
         patch("eco.pipeline.nomear_narrativa", return_value=fake_nome), \
         patch("eco.pipeline.revisar_classificacao", return_value=fake_review), \
         patch("eco.pipeline._dispara_veritas") as mock_dispara:
        state = rodar_eco(janela_horas=6)
    assert state["status"] == "concluido"
    assert len(state["narrativas"]) == 1
    assert state["narrativas"][0].classificacao == "coordenado"
    mock_dispara.assert_called_once()
