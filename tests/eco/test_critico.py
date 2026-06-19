from unittest.mock import patch
from eco.agentes.critico import revisar_classificacao
from core.modelos import Narrativa
from pydantic import BaseModel


class FakeRevisao(BaseModel):
    aprova: bool
    problemas: list[str]
    sugestao: str = ""


def test_revisar_classificacao_aprova():
    narrativa = Narrativa(
        cluster_id="c1", nome="X ligado a Y", descricao="narrativa",
        volume=10, velocidade_crescimento=1.0, classificacao="coordenado",
        confianca=0.85, justificativa="8 contas em 12min",
        candidatos_afetados=["X"], primeiro_post_em="2026-06-18T10:00:00",
    )
    fake = FakeRevisao(aprova=True, problemas=[])
    with patch("eco.agentes.critico.gerar_resposta", return_value=fake):
        revisao = revisar_classificacao(narrativa)
    assert revisao["aprova"] is True
    assert revisao["problemas"] == []


def test_revisar_classificacao_rejeita():
    narrativa = Narrativa(
        cluster_id="c1", nome="vago", descricao="narrativa vaga",
        volume=10, velocidade_crescimento=1.0, classificacao="coordenado",
        confianca=0.85, justificativa="",
        candidatos_afetados=[], primeiro_post_em="",
    )
    fake = FakeRevisao(aprova=False, problemas=["justificativa vazia", "candidatos faltando"])
    with patch("eco.agentes.critico.gerar_resposta", return_value=fake):
        revisao = revisar_classificacao(narrativa)
    assert revisao["aprova"] is False
    assert len(revisao["problemas"]) == 2
