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


def test_eco_analyze_post_enfileira_job(db, client):
    resp = client.post("/eco/analyze", data={"janela_horas": "12"})
    assert resp.status_code == 302, f"expected redirect, got {resp.status_code}"
    assert "/eco/" in resp.headers["Location"]


def test_eco_analyze_post_default_janela(db, client):
    resp = client.post("/eco/analyze", data={})
    assert resp.status_code == 302
    import sqlite3
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT tipo, payload FROM job_queue WHERE modulo='eco' ORDER BY id DESC LIMIT 1").fetchone()
    assert row is not None
    assert row[0] == "eco_analyze"
    import json
    payload = json.loads(row[1])
    assert payload["janela_horas"] == 24


def test_eco_analyze_post_janela_invalida_usa_default(db, client):
    resp = client.post("/eco/analyze", data={"janela_horas": "abc"})
    assert resp.status_code == 302
    import sqlite3, json
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT payload FROM job_queue WHERE modulo='eco' ORDER BY id DESC LIMIT 1").fetchone()
    assert row is not None
    payload = json.loads(row[0])
    assert payload["janela_horas"] == 24


def test_eco_analyze_post_clamp_janela_max_168(db, client):
    resp = client.post("/eco/analyze", data={"janela_horas": "99999"})
    assert resp.status_code == 302
    import sqlite3, json
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT payload FROM job_queue WHERE modulo='eco' ORDER BY id DESC LIMIT 1").fetchone()
    payload = json.loads(row[0])
    assert payload["janela_horas"] == 168


def test_eco_coleta_post_sem_handle(db, client):
    resp = client.post("/eco/coleta", data={})
    assert resp.status_code == 302
    import sqlite3, json
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT tipo, payload FROM job_queue WHERE modulo='eco' ORDER BY id DESC LIMIT 1").fetchone()
    assert row[0] == "eco_coleta"
    payload = json.loads(row[1])
    assert "instagram_handle" not in payload
    assert payload["limite"] == 20


def test_eco_coleta_post_com_handle(db, client):
    resp = client.post("/eco/coleta", data={"instagram_handle": "@canal_x", "limite": "50"})
    assert resp.status_code == 302
    import sqlite3, json
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT payload FROM job_queue WHERE modulo='eco' ORDER BY id DESC LIMIT 1").fetchone()
    payload = json.loads(row[0])
    assert payload["instagram_handle"] == "@canal_x"
    assert payload["limite"] == 50


def test_eco_analyze_get_nao_suportado(db, client):
    """GET /eco/analyze deve retornar 405 (apenas POST)."""
    resp = client.get("/eco/analyze")
    assert resp.status_code == 405


def test_eco_lista_mostra_recent_jobs(db, client):
    import sqlite3, json
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO job_queue (modulo, tipo, payload, status, criado_em) "
        "VALUES ('eco', 'eco_analyze', ?, 'done', datetime('now'))",
        (json.dumps({"janela_horas": 24}),),
    )
    conn.commit()
    conn.close()
    resp = client.get("/eco/")
    assert resp.status_code == 200
    assert b"eco_analyze" in resp.data
    assert b"done" in resp.data


def test_eco_lista_mostra_botao_rodar_analise(db, client):
    resp = client.get("/eco/")
    assert resp.status_code == 200
    assert b"Rodar an" in resp.data or b"Rodar an\u00e1" in resp.data
    assert b"eco_analyze" in resp.data or b"action=" in resp.data

