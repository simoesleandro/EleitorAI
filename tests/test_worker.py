from worker.pipeline import run_once, schedule_jobs, recover_stuck_jobs
from core.fila import enqueue


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


def test_recover_stuck_jobs_resets_old_running(db):
    from core.db import get_db

    conn = get_db(db_path=db)
    cursor = conn.execute(
        "INSERT INTO job_queue (modulo, tipo, payload, status, iniciado_em) "
        "VALUES (?, ?, ?, 'running', datetime('now', '-1 hour'))",
        ("veritas", "veritas_check", "{}"),
    )
    conn.commit()
    stuck_id = cursor.lastrowid
    conn.close()

    recovered = recover_stuck_jobs(timeout_minutes=30)
    assert recovered == 1

    conn = get_db(db_path=db)
    row = conn.execute("SELECT status, iniciado_em FROM job_queue WHERE id=?", (stuck_id,)).fetchone()
    conn.close()
    assert row["status"] == "pending"
    assert row["iniciado_em"] is None


def test_recover_stuck_jobs_keeps_recent_running(db):
    from core.db import get_db

    conn = get_db(db_path=db)
    cursor = conn.execute(
        "INSERT INTO job_queue (modulo, tipo, payload, status, iniciado_em) "
        "VALUES (?, ?, ?, 'running', datetime('now', '-5 minutes'))",
        ("veritas", "veritas_check", "{}"),
    )
    conn.commit()
    recent_id = cursor.lastrowid
    conn.close()

    recovered = recover_stuck_jobs(timeout_minutes=30)
    assert recovered == 0

    conn = get_db(db_path=db)
    row = conn.execute("SELECT status FROM job_queue WHERE id=?", (recent_id,)).fetchone()
    conn.close()
    assert row["status"] == "running"
