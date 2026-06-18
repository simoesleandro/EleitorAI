import os
import tempfile
import sqlite3
import pytest
from core.db import init_db, get_db


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    init_db(db_path)
    return db_path


def test_init_db_creates_all_tables(tmp_db):
    conn = get_db(db_path=tmp_db)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row["name"] for row in cursor.fetchall()]
    expected = [
        "afirmacoes", "alertas", "amplificadores", "briefings",
        "candidatos", "checagens", "debates", "falas", "fontes",
        "job_queue", "mencoes", "momentos_virais", "narrativas",
        "relacoes_amplificacao", "scheduler_log", "usuarios",
    ]
    for t in expected:
        assert t in tables, f"tabela {t} não foi criada"
    conn.close()


def test_get_db_returns_connection_with_row_factory(tmp_db):
    conn = get_db(db_path=tmp_db)
    assert conn.row_factory == sqlite3.Row
    conn.close()


def test_init_db_is_idempotent(tmp_db):
    init_db(db_path=tmp_db)
    init_db(db_path=tmp_db)
    conn = get_db(db_path=tmp_db)
    cursor = conn.execute("SELECT COUNT(*) as c FROM candidatos")
    assert cursor.fetchone()["c"] == 0
    conn.close()


def test_embeddings_virtual_table_uses_vec0(tmp_db):
    conn = get_db(db_path=tmp_db)
    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name='embeddings'")
    sql = cursor.fetchone()["sql"]
    assert "vec0" in sql.lower()
    conn.close()
