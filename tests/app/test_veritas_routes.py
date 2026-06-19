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


def test_veritas_pdf_retorna_pdf_quando_gerar_sucesso(client):
    from unittest.mock import patch
    from core.db import get_db
    conn = get_db()
    fonte_id = conn.execute(
        "INSERT INTO fontes (tipo, identificador, nome, coletor) VALUES (?, ?, ?, ?)",
        ("rss", "src", "fonte", "manual"),
    ).lastrowid
    cand_id = conn.execute(
        "INSERT INTO candidatos (nome, partido, cargo) VALUES (?, ?, ?)",
        ("X", "P", "governador"),
    ).lastrowid
    mencao_id = conn.execute(
        """INSERT INTO mencoes (fonte_id, candidato_id, texto, autor, autor_id, timestamp, hash_conteudo)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (fonte_id, cand_id, "m", "a", "0", "2026-01-01T00:00:00", "h1"),
    ).lastrowid
    af_id = conn.execute(
        "INSERT INTO afirmacoes (mencao_id, texto) VALUES (?, ?)",
        (mencao_id, "claim teste"),
    ).lastrowid
    ch_id = conn.execute(
        """INSERT INTO checagens (afirmacao_id, veredito, evidencias, fontes_independentes, confianca, justificativa, modelo)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (af_id, "verdadeiro", "[]", 1, 0.9, "j", "gemini"),
    ).lastrowid
    conn.commit()
    conn.close()

    with patch("veritas.dossie.gerar_dossie_pdf", return_value=b"%PDF-fake"):
        resp = client.get(f"/veritas/{ch_id}/pdf")
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"


def test_veritas_pdf_retorna_md_quando_gerar_falha(client):
    from unittest.mock import patch
    from core.db import get_db
    conn = get_db()
    fonte_id = conn.execute(
        "INSERT INTO fontes (tipo, identificador, nome, coletor) VALUES (?, ?, ?, ?)",
        ("rss", "src", "fonte", "manual"),
    ).lastrowid
    cand_id = conn.execute(
        "INSERT INTO candidatos (nome, partido, cargo) VALUES (?, ?, ?)",
        ("X", "P", "governador"),
    ).lastrowid
    mencao_id = conn.execute(
        """INSERT INTO mencoes (fonte_id, candidato_id, texto, autor, autor_id, timestamp, hash_conteudo)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (fonte_id, cand_id, "m", "a", "0", "2026-01-01T00:00:00", "h1"),
    ).lastrowid
    af_id = conn.execute(
        "INSERT INTO afirmacoes (mencao_id, texto) VALUES (?, ?)",
        (mencao_id, "claim teste"),
    ).lastrowid
    ch_id = conn.execute(
        """INSERT INTO checagens (afirmacao_id, veredito, evidencias, fontes_independentes, confianca, justificativa, modelo)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (af_id, "verdadeiro", "[]", 1, 0.9, "j", "gemini"),
    ).lastrowid
    conn.commit()
    conn.close()

    with patch("veritas.dossie.gerar_dossie_pdf", side_effect=NotImplementedError("no pdf engine")):
        resp = client.get(f"/veritas/{ch_id}/pdf")
    assert resp.status_code == 200
    assert resp.mimetype == "text/markdown"


def test_veritas_pdf_404_quando_checagem_nao_existe(client):
    resp = client.get("/veritas/9999/pdf")
    assert resp.status_code == 404
