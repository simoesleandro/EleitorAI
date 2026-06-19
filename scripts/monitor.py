"""Background monitor: polls EleitorAI state and writes JSON status file.

Runs as a Start-Job so it never blocks the parent process. Updates
data/status.json every N seconds until killed.

Usage:
    powershell -Command "Start-Job -ScriptBlock { python scripts/monitor.py }"

Output: data/status.json with current state
"""
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path

DB = Path(r"C:\Meus_projetos\vox-plataforma\eleitorai\data\eleitorai.db")
OUT = Path(r"C:\Meus_projetos\vox-plataforma\eleitorai\data\status.json")
INTERVAL = 10  # seconds
MAX_ITERATIONS = 360  # 1 hour


def snapshot():
    if not DB.exists():
        return {"error": f"DB not found: {DB}"}
    try:
        conn = sqlite3.connect(str(DB), timeout=2)
        cur = conn.cursor()
        jobs = [dict(zip(["id", "tipo", "status", "criado_em", "concluido_em"], r))
                for r in cur.execute(
                    "SELECT id, tipo, status, criado_em, concluido_em FROM job_queue "
                    "WHERE modulo='eco' ORDER BY id DESC LIMIT 10"
                ).fetchall()]
        mencoes = cur.execute("SELECT COUNT(*) FROM mencoes").fetchone()[0]
        narrativas = cur.execute("SELECT COUNT(*) FROM narrativas").fetchone()[0]
        mencoes_recentes = cur.execute(
            "SELECT id, autor, substr(texto,1,60) FROM mencoes "
            "WHERE timestamp > datetime('now', '-1 day') ORDER BY id DESC LIMIT 3"
        ).fetchall()
        fontes_tg = cur.execute(
            "SELECT COUNT(*) FROM fontes WHERE tipo='telegram' AND ativa=1"
        ).fetchone()[0]
        conn.close()
        return {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "jobs": jobs,
            "jobs_pending": sum(1 for j in jobs if j["status"] == "pending"),
            "jobs_running": sum(1 for j in jobs if j["status"] == "running"),
            "jobs_done": sum(1 for j in jobs if j["status"] == "done"),
            "jobs_failed": sum(1 for j in jobs if j["status"] == "failed"),
            "mencoes_total": mencoes,
            "mencoes_recentes_24h": [dict(zip(["id", "autor", "preview"], r)) for r in mencoes_recentes],
            "narrativas_total": narrativas,
            "fontes_telegram_ativas": fontes_tg,
        }
    except Exception as e:
        return {"ts": datetime.now().isoformat(timespec="seconds"), "error": str(e)}


def main():
    for i in range(MAX_ITERATIONS):
        snap = snapshot()
        OUT.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
