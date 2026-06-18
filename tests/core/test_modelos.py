import pytest
from pydantic import ValidationError
from core.modelos import (
    Mencao, Afirmacao, Checagem, Evidencia, Alerta, Job, Candidato, Fonte,
)


def test_mencao_minimal():
    m = Mencao(fonte_id=1, texto="hello", timestamp="2026-06-18T10:00:00", hash_conteudo="abc")
    assert m.fonte_id == 1
    assert m.texto == "hello"
    assert m.metricas == {}
    assert m.id is None
    assert m.candidato_id is None


def test_afirmacao_checavel_default_true():
    a = Afirmacao(mencao_id=1, texto="zero crescimento")
    assert a.checavel is True
    assert a.confianca_extracao is None


def test_checagem_veredito_invalid_raises():
    with pytest.raises(ValidationError):
        Checagem(
            afirmacao_id=1,
            veredito="invalido",
            evidencias=[],
            fontes_independentes=0,
            confianca=0.5,
        )


def test_checagem_valid():
    ev = Evidencia(fonte="IBGE", trecho="cresceu 8.2%", url="https://ibge.gov.br")
    c = Checagem(
        afirmacao_id=1,
        veredito="falso",
        evidencias=[ev, ev],
        fontes_independentes=2,
        confianca=0.9,
        justificativa="afirmacao contradiz Censo 2022",
        contraposicao_sugerida="cresceu 8.2%",
        modelo="gemini",
    )
    assert c.veredito == "falso"
    assert len(c.evidencias) == 2


def test_alerta_severidade_validation():
    with pytest.raises(ValidationError):
        Alerta(modulo="veritas", severidade="invalido", titulo="x", payload={})


def test_alerta_valid():
    a = Alerta(modulo="veritas", severidade="alto", titulo="claim falsa", payload={"id": 1})
    assert a.severidade == "alto"
    assert a.enviado_telegram is False


def test_job_status_pending_default():
    j = Job(modulo="veritas", tipo="veritas_check", payload={})
    assert j.status == "pending"
    assert j.resultado is None


def test_candidato_defaults():
    c = Candidato(nome="Fulano", cargo="presidente")
    assert c.eh_proprio is False
    assert c.monitorar_veritas is True
    assert c.monitorar_eco is True


def test_fonte_tipo_validation():
    f = Fonte(tipo="telegram", identificador="@canal", coletor="core.coletores.telegram")
    assert f.ativa is True
    assert f.config == {}
