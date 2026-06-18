import pytest


@pytest.fixture
def db(tmp_path, monkeypatch):
    from core.config import get_settings
    from core.db import init_db

    get_settings.cache_clear()
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    init_db(db_path)
    return db_path


def test_conftest_db_fixture_is_available(db):
    assert db.endswith(".db")
