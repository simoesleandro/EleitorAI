import pytest
from app import create_app


@pytest.fixture
def client(monkeypatch, tmp_path):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    from core.db import init_db
    init_db(str(tmp_path / "test.db"))
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_dashboard_returns_200(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"EleitorAI" in resp.data


def test_root_redirects_to_dashboard(client):
    resp = client.get("/")
    assert resp.status_code in (302, 301)


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    import json
    data = json.loads(resp.data)
    assert data["status"] == "ok"
