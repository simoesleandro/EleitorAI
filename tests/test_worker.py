import pytest
from worker.pipeline import run_once, schedule_jobs
from core.db import init_db
from core.fila import enqueue


@pytest.fixture
def db(tmp_path, monkeypatch):
    from core.config import get_settings
    get_settings.cache_clear()
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    init_db(db_path)
    return db_path


def test_run_once_no_jobs_returns_zero(db):
    processed = run_once()
    assert processed == 0


def test_run_once_processes_pending_job(db):
    from worker.pipeline import register_handler
    register_handler("veritas_check", lambda payload: {"ok": True})
    enqueue("veritas", "veritas_check", {"test": True})
    processed = run_once()
    assert processed == 1


def test_schedule_jobs_returns_scheduler(db):
    sched = schedule_jobs()
    assert sched is not None
    sched.shutdown(wait=False)
