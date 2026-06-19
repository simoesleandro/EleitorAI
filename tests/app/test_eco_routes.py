import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    from core.config import get_settings
    from core.db import init_db
    get_settings.cache_clear()
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    init_db(db_path)
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


def test_eco_lista_renderiza(db, client):
    resp = client.get("/eco/")
    assert resp.status_code == 200
    assert b"Narrativas" in resp.data


def test_eco_detalhe_404_quando_nao_existe(db, client):
    resp = client.get("/eco/9999")
    assert resp.status_code == 404


def test_eco_grafo_404_quando_nao_existe(db, client):
    resp = client.get("/eco/9999/grafo")
    assert resp.status_code == 404
