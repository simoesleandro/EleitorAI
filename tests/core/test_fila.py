import pytest
from core.config import get_settings
from core.db import init_db
from core.fila import enqueue, dequeue, complete_job, fail_job, list_pending


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    get_settings.cache_clear()
    init_db(db_path)
    return db_path


def test_enqueue_returns_id(db):
    job_id = enqueue("veritas", "veritas_check", {"video_id": "abc"})
    assert isinstance(job_id, int)
    assert job_id > 0


def test_dequeue_returns_oldest_pending(db):
    jid1 = enqueue("veritas", "veritas_check", {"a": 1})
    jid2 = enqueue("eco", "eco_analyze", {"b": 2})
    job = dequeue()
    assert job.id == jid1
    assert job.status == "running"
    job2 = dequeue()
    assert job2.id == jid2


def test_dequeue_empty_returns_none(db):
    assert dequeue() is None


def test_complete_job_marks_done(db):
    jid = enqueue("veritas", "veritas_check", {})
    dequeue()
    complete_job(jid, {"veredito": "falso"})
    from core.fila import get_job
    j = get_job(jid)
    assert j.status == "done"
    assert j.resultado == {"veredito": "falso"}
    assert j.concluido_em is not None


def test_fail_job_marks_failed(db):
    jid = enqueue("veritas", "veritas_check", {})
    dequeue()
    fail_job(jid, "API timeout")
    from core.fila import get_job
    j = get_job(jid)
    assert j.status == "failed"
    assert j.resultado == {"erro": "API timeout"}


def test_list_pending(db):
    enqueue("veritas", "veritas_check", {})
    enqueue("eco", "eco_analyze", {})
    pending = list_pending()
    assert len(pending) == 2
    dequeue()
    pending = list_pending()
    assert len(pending) == 1
