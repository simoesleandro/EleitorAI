import pytest
from unittest.mock import patch, MagicMock
from core.db import init_db
from core.coletores.telegram import _to_mencao
from core.modelos import Mencao


@pytest.fixture
def db(tmp_path, monkeypatch):
    from core.config import get_settings
    get_settings.cache_clear()
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    init_db(db_path)
    monkeypatch.setenv("TELEGRAM_API_ID", "11111")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    return db_path


def test_to_mencao_mapeia_mensagem_telegram(db):
    mock_msg = MagicMock()
    mock_msg.id = 42
    mock_msg.text = "candidato X ligado a esquema Y"
    mock_msg.date.isoformat.return_value = "2026-06-18T10:00:00"
    mock_msg.sender.username = "joao"
    mock_msg.sender_id = 123
    mock_msg.fwd_from = None

    mencao = _to_mencao(mock_msg, fonte_id=1)
    assert isinstance(mencao, Mencao)
    assert mencao.texto == "candidato X ligado a esquema Y"
    assert mencao.autor == "joao"
    assert mencao.autor_id == "123"
    assert mencao.hash_conteudo


def test_to_mencao_captura_forward_info(db):
    mock_msg = MagicMock()
    mock_msg.id = 42
    mock_msg.text = "mensagem forwardada"
    mock_msg.date.isoformat.return_value = "2026-06-18T10:00:00"
    mock_msg.sender.username = "canal2"
    mock_msg.sender_id = 999
    mock_msg.fwd_from = MagicMock()
    mock_msg.fwd_from.from_id = MagicMock()
    mock_msg.fwd_from.from_id.channel_id = 111

    mencao = _to_mencao(mock_msg, fonte_id=1)
    assert "forwarded_from" in mencao.metricas
    assert mencao.metricas["forwarded_from"] == 111
