import pytest
from app import create_app
from core.db import init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setenv("SECRET_KEY", "x")
    init_db(str(tmp_path / "t.db"))
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_veritas_lista_retorna_200(client):
    resp = client.get("/veritas/")
    assert resp.status_code == 200
    assert b"Veritas" in resp.data


def test_veritas_novo_enfila_job(client):
    from unittest.mock import patch
    with patch("app.routes.veritas.enqueue", return_value=42) as mock_enq:
        resp = client.post("/veritas/novo", data={"conteudo": "texto teste"})
    assert resp.status_code in (302, 201)
    mock_enq.assert_called_once()
