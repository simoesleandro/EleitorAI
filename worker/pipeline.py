import logging
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler

from core.db import get_db, init_db
from core.fila import dequeue, complete_job, fail_job

from worker.jobs_veritas import job_veritas_check, job_veritas_seed, job_veritas_atualiza_base

logger = logging.getLogger(__name__)

_JOB_HANDLERS: dict[str, Callable] = {}


def register_handler(tipo: str, fn: Callable) -> None:
    _JOB_HANDLERS[tipo] = fn


register_handler("veritas_check", job_veritas_check)
register_handler("veritas_seed", job_veritas_seed)
register_handler("veritas_atualiza_base", job_veritas_atualiza_base)


def recover_stuck_jobs(timeout_minutes: int = 30) -> int:
    conn = get_db()
    try:
        cursor = conn.execute(
            "UPDATE job_queue SET status='pending', iniciado_em=NULL "
            "WHERE status='running' AND iniciado_em < datetime('now', ?)",
            (f"-{timeout_minutes} minutes",),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def run_once() -> int:
    recover_stuck_jobs()
    processed = 0
    while True:
        job = dequeue()
        if job is None:
            break
        handler = _JOB_HANDLERS.get(job.tipo)
        if handler is None:
            fail_job(job.id, f"sem handler para tipo {job.tipo}")
            continue
        try:
            resultado = handler(job.payload)
            complete_job(job.id, resultado or {})
            processed += 1
        except Exception as e:
            logger.error(f"job {job.id} falhou: {e}")
            fail_job(job.id, str(e))
    return processed


def schedule_jobs() -> BackgroundScheduler:
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_once, "interval", minutes=1, id="process_queue")
    scheduler.start()
    return scheduler


def run_daemon() -> None:
    scheduler = schedule_jobs()
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
