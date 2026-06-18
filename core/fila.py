import json
from datetime import datetime
from typing import Optional

from core.db import get_db
from core.modelos import Job, Modulo


def enqueue(modulo: Modulo, tipo: str, payload: dict) -> int:
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO job_queue (modulo, tipo, payload, status) VALUES (?, ?, ?, 'pending')",
            (modulo, tipo, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def dequeue() -> Optional[Job]:
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.execute(
            "SELECT * FROM job_queue WHERE status='pending' ORDER BY id LIMIT 1"
        )
        row = cursor.fetchone()
        if row is None:
            conn.execute("ROLLBACK")
            return None
        now = _now()
        conn.execute(
            "UPDATE job_queue SET status='running', iniciado_em=? WHERE id=?",
            (now, row["id"]),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM job_queue WHERE id=?", (row["id"],)).fetchone()
        return _row_to_job(row)
    finally:
        conn.close()


def complete_job(job_id: int, resultado: dict) -> None:
    conn = get_db()
    try:
        now = _now()
        conn.execute(
            "UPDATE job_queue SET status='done', resultado=?, concluido_em=? WHERE id=?",
            (json.dumps(resultado, ensure_ascii=False), now, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def fail_job(job_id: int, erro: str) -> None:
    conn = get_db()
    try:
        now = _now()
        conn.execute(
            "UPDATE job_queue SET status='failed', resultado=?, concluido_em=? WHERE id=?",
            (json.dumps({"erro": erro}, ensure_ascii=False), now, job_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: int) -> Optional[Job]:
    conn = get_db()
    try:
        cursor = conn.execute("SELECT * FROM job_queue WHERE id=?", (job_id,))
        row = cursor.fetchone()
        return _row_to_job(row) if row else None
    finally:
        conn.close()


def list_pending() -> list[Job]:
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT * FROM job_queue WHERE status='pending' ORDER BY id"
        )
        return [_row_to_job(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _row_to_job(row) -> Job:
    return Job(
        id=row["id"],
        modulo=row["modulo"],
        tipo=row["tipo"],
        payload=json.loads(row["payload"]) if row["payload"] else {},
        status=row["status"],
        resultado=json.loads(row["resultado"]) if row["resultado"] else None,
        criado_em=row["criado_em"],
        iniciado_em=row["iniciado_em"],
        concluido_em=row["concluido_em"],
    )
