import pytest
from pydantic import ValidationError
from core.modelos import (
    Cluster, Narrativa, Amplificador, RelacaoAmplificacao, ClassificacaoNarrativa
)


def test_classificacao_narrativa_literal():
    assert ClassificacaoNarrativa.__origin__ is not None


def test_cluster_minimal():
    c = Cluster(id="c1", mencao_ids=[1, 2, 3], centroide_texto="crescimento", volume=3)
    assert c.volume == 3


def test_narrativa_valid():
    n = Narrativa(
        cluster_id="c1", nome="candidato X ligado a Y", descricao="narrativa de corrupcao",
        volume=100, velocidade_crescimento=3.2, classificacao="coordenado",
        confianca=0.85, justificativa="8 contas em 12min",
        candidatos_afetados=["X"], primeiro_post_em="2026-06-18T10:00:00"
    )
    assert n.classificacao == "coordenado"


def test_narrativa_classificacao_invalida_raises():
    with pytest.raises(ValidationError):
        Narrativa(
            cluster_id="c1", nome="x", descricao="x", volume=1, velocidade_crescimento=1.0,
            classificacao="invalido", confianca=0.5, justificativa="",
            candidatos_afetados=[], primeiro_post_em=""
        )


def test_amplificador_defaults():
    a = Amplificador(identificador="@canal", tipo="telegram_channel", centralidade=0.8)
    assert a.suspeita_bot is False
    assert a.idade_conta_dias is None


def test_relacao_amplificacao_valid():
    r = RelacaoAmplificacao(
        de_identificador="@a", para_identificador="@b", peso=0.9,
        janela_minutos=5, tipo="forward"
    )
    assert r.tipo == "forward"
