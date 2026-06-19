"""Tests for worker PID/file lock (Fix C: OS-level file lock).

The lock must be released automatically when the process dies, even if killed
with SIGKILL (taskkill /F, Stop-Process -Force), so a new worker can start
without manual cleanup of worker.pid.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def isolated_lock(tmp_path, monkeypatch):
    """Isolated lock files + guaranteed cleanup of module-global state."""
    import worker.__main__ as m

    pid_file = tmp_path / "worker.pid"
    lock_file = tmp_path / "worker.lock"
    monkeypatch.setattr(m, "_PID_FILE", pid_file)
    monkeypatch.setattr(m, "_LOCK_FILE", lock_file)

    # Reset module-global _lock_handle before each test
    monkeypatch.setattr(m, "_lock_handle", None)

    yield {"pid_file": pid_file, "lock_file": lock_file, "module": m}

    # Cleanup: release lock + close handle if still held
    try:
        m._release_lock()
    except Exception:
        pass
    for f in (pid_file, lock_file):
        try:
            f.unlink()
        except FileNotFoundError:
            pass


def test_acquire_lock_creates_pid_file(isolated_lock):
    from worker.__main__ import _acquire_lock

    _acquire_lock()
    assert isolated_lock["pid_file"].exists()
    assert isolated_lock["pid_file"].read_text() == str(os.getpid())


def test_acquire_lock_blocks_second_caller_when_lock_held(isolated_lock):
    """A second acquire in the same process must fail (lock already held)."""
    from worker.__main__ import _acquire_lock

    _acquire_lock()
    with pytest.raises(SystemExit):
        _acquire_lock()


def test_lock_released_on_clean_exit(isolated_lock):
    from worker.__main__ import _acquire_lock, _release_lock

    _acquire_lock()
    _release_lock()
    assert not isolated_lock["pid_file"].exists()


def _spawn_child_acquiring_lock(pid_file, lock_file, ready_file, hold_seconds=60):
    """Spawn a child process that acquires the lock and blocks.

    Returns the Popen object. The child writes `ready_file` once it has
    acquired the lock, then sleeps for `hold_seconds`.
    """
    project_root = str(_PROJECT_ROOT)
    child_script = (
        "import sys, os, time\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, r'{project_root}')\n"
        "import worker.__main__ as m\n"
        f"m._PID_FILE = Path(r'{pid_file}')\n"
        f"m._LOCK_FILE = Path(r'{lock_file}')\n"
        "m._acquire_lock()\n"
        f"open(r'{ready_file}', 'w').close()\n"
        f"time.sleep({hold_seconds})\n"
    )
    return subprocess.Popen(
        [sys.executable, "-c", child_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _wait_for_ready(proc, ready_file, timeout=10):
    """Wait until `ready_file` appears or `proc` dies / timeout expires."""
    deadline = time.time() + timeout
    while not ready_file.exists() and time.time() < deadline:
        if proc.poll() is not None:
            out, err = proc.communicate(timeout=1)
            pytest.fail(f"child died early: {err.decode()}")
        time.sleep(0.1)
    assert ready_file.exists(), f"child did not signal ready within {timeout}s"


def test_lock_released_when_process_killed(tmp_path):
    """Fix C core requirement: lock must release on SIGKILL.

    Spawns a child that acquires the lock, then SIGKILLs it. A second process
    must be able to acquire the lock immediately afterward without any manual
    PID-file cleanup. This is the OS-level file lock guarantee.
    """
    pid_file = tmp_path / "worker.pid"
    lock_file = tmp_path / "worker.lock"
    ready_file = tmp_path / "ready.flag"

    proc = _spawn_child_acquiring_lock(pid_file, lock_file, ready_file)
    try:
        _wait_for_ready(proc, ready_file)
        assert pid_file.exists()
        # Note: pid_file content may differ from proc.pid on Windows venv
        # (venv launcher re-executes base python as a child process).
        # We don't assert the PID value here, only that the file exists.

        # Kill the child HARD (SIGKILL equivalent) - no finally block runs.
        proc.kill()
        proc.wait(timeout=5)

        # A second process must now be able to acquire the lock, even though
        # the stale pid_file may still exist on disk. This is the Fix C
        # guarantee: the OS releases the file lock on process death
        # regardless of stale pid file content.
        project_root = str(_PROJECT_ROOT)
        second_script = (
            "import sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0, r'{project_root}')\n"
            "import worker.__main__ as m\n"
            f"m._PID_FILE = Path(r'{pid_file}')\n"
            f"m._LOCK_FILE = Path(r'{lock_file}')\n"
            "m._acquire_lock()\n"
            "print('ACQUIRED')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", second_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"second process could not acquire lock after kill: "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        assert "ACQUIRED" in result.stdout
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)


def test_lock_blocks_second_process_while_first_alive(tmp_path):
    """While the first process holds the lock, a second must exit with error."""
    pid_file = tmp_path / "worker.pid"
    lock_file = tmp_path / "worker.lock"
    ready_file = tmp_path / "ready.flag"

    proc = _spawn_child_acquiring_lock(pid_file, lock_file, ready_file)
    try:
        _wait_for_ready(proc, ready_file)

        project_root = str(_PROJECT_ROOT)
        second_script = (
            "import sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0, r'{project_root}')\n"
            "import worker.__main__ as m\n"
            f"m._PID_FILE = Path(r'{pid_file}')\n"
            f"m._LOCK_FILE = Path(r'{lock_file}')\n"
            "m._acquire_lock()\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", second_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0, (
            "second process should have exited with error, but succeeded: "
            f"stdout={result.stdout!r}"
        )
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)


def test_lock_works_with_preexisting_lock_file_content(tmp_path):
    """Lock must work even when worker.lock already exists with content.

    The OS file lock is independent of file content - it operates on the
    file handle, not the bytes. A stale lock file with old content must
    not prevent a new process from acquiring the lock.
    """
    pid_file = tmp_path / "worker.pid"
    lock_file = tmp_path / "worker.lock"
    ready_file = tmp_path / "ready.flag"

    # Pre-populate the lock file with stale content
    lock_file.write_bytes(b"X" * 16)

    proc = _spawn_child_acquiring_lock(pid_file, lock_file, ready_file)
    try:
        _wait_for_ready(proc, ready_file)
        assert pid_file.exists()

        # While the first process holds the lock, a second must still fail
        project_root = str(_PROJECT_ROOT)
        second_script = (
            "import sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0, r'{project_root}')\n"
            "import worker.__main__ as m\n"
            f"m._PID_FILE = Path(r'{pid_file}')\n"
            f"m._LOCK_FILE = Path(r'{lock_file}')\n"
            "m._acquire_lock()\n"
            "print('ACQUIRED')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", second_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0, (
            "second process should have been blocked by held lock, "
            f"but succeeded: stdout={result.stdout!r}"
        )
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
