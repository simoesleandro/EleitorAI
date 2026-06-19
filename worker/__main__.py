import argparse
import logging
import os
import sys
from pathlib import Path

from core.logging_redactor import install_redactor
from worker.pipeline import run_daemon, run_once

_PID_FILE = Path(__file__).resolve().parent.parent / "worker.pid"
_LOCK_FILE = Path(__file__).resolve().parent.parent / "worker.lock"

if sys.platform == "win32":
    import msvcrt

    def _lock_file(fh):
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock_file(fh):
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:
    import fcntl

    def _lock_file(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_file(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


_lock_handle = None


def _acquire_lock():
    global _lock_handle
    if _lock_handle is not None:
        print("Worker already running in this process. Exiting.", file=sys.stderr)
        sys.exit(1)
    try:
        _lock_handle = open(_LOCK_FILE, "a+b")
        _lock_file(_lock_handle)
    except OSError:
        old_pid = _PID_FILE.read_text().strip() if _PID_FILE.exists() else "?"
        print(f"Worker already running (PID {old_pid}). Exiting.", file=sys.stderr)
        sys.exit(1)
    _PID_FILE.write_text(str(os.getpid()))
    logging.info(f"Worker lock acquired (PID {os.getpid()})")


def _release_lock():
    global _lock_handle
    if _lock_handle is not None:
        _unlock_file(_lock_handle)
        _lock_handle.close()
        _lock_handle = None
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
