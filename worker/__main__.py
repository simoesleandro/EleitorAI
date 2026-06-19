import argparse
import logging
import os
import sys
from pathlib import Path

from core.logging_redactor import install_redactor
from worker.pipeline import run_daemon, run_once

_PID_FILE = Path(__file__).resolve().parent.parent / "worker.pid"


def _acquire_lock():
    if _PID_FILE.exists():
        old_pid = _PID_FILE.read_text().strip()
        try:
            os.kill(int(old_pid), 0)
            print(f"Worker already running (PID {old_pid}). Exiting.", file=sys.stderr)
            sys.exit(1)
        except (ProcessLookupError, ValueError, OSError):
            _PID_FILE.unlink(missing_ok=True)
    _PID_FILE.write_text(str(os.getpid()))


def _release_lock():
    _PID_FILE.unlink(missing_ok=True)


install_redactor()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main():
    _acquire_lock()
    parser = argparse.ArgumentParser(description="EleitorAI worker")
    parser.add_argument("--daemon", action="store_true", help="roda em modo daemon continuo")
    parser.add_argument("--once", action="store_true", help="processa fila uma vez")
    args = parser.parse_args()
    try:
        if args.daemon:
            run_daemon()
        elif args.once:
            processed = run_once()
            print(f"processados: {processed}")
        else:
            parser.print_help()
    finally:
        _release_lock()


if __name__ == "__main__":
    main()
