from unittest.mock import patch
from eco.agentes.caracterizador import caracterizar_narrativa
from core.modelos import Cluster
from pydantic import BaseModel


class FakeResult(BaseModel):
    classificacao: str
    justificativa: str
    confianca: float


def test_caracterizar_narrativa_retorna_classificacao():
    cluster = Cluster(id="c1", mencao_ids=[1, 2, 3], centroide_texto="x", volume=3)
    features = {"num_contas": 10, "max_degree": 8, "densidade": 0.7, "suspeitos_bot": 0, "contas_jovens": 0}
    fake = FakeResult(classificacao="coordenado", justificativa="8 contas em janela curta", confianca=0.85)
    with patch("eco.agentes.caracterizador.gerar_resposta", return_value=fake):
        classificacao, justificativa, confianca = caracterizar_narrativa(cluster, features)
    assert classificacao == "coordenado"
    assert "8 contas" in justificativa
    assert confianca == 0.85
