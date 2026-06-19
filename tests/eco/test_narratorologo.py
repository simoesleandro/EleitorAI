from unittest.mock import patch
from eco.agentes.narratorologo import nomear_narrativa
from core.modelos import Cluster
from pydantic import BaseModel


class FakeResult(BaseModel):
    nome: str
    descricao: str
    candidatos_afetados: list[str]


def test_nomear_narrativa_retorna_nome_descricao_candidatos():
    cluster = Cluster(id="c1", mencao_ids=[1, 2, 3], centroide_texto="candidato X ligado a Y", volume=3)
    fake = FakeResult(
        nome="Candidato X ligado a Y",
        descricao="Multiplas contas associam X a Y",
        candidatos_afetados=["X"],
    )
    with patch("eco.agentes.narratorologo.gerar_resposta", return_value=fake):
        nome, descricao, candidatos = nomear_narrativa(cluster, "coordenado")
    assert nome == "Candidato X ligado a Y"
    assert "X" in descricao
    assert candidatos == ["X"]
