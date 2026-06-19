"""Tests for the pre-commit hook script (scripts/check_no_env.py)."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_no_env.py"


def _run_with_staged(tmp_path, staged_files: list[str]) -> subprocess.CompletedProcess:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo, check=True, stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=repo, check=True, stdout=subprocess.DEVNULL,
    )
    for fname in staged_files:
        f = repo / fname
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("content")
        subprocess.run(["git", "add", fname], cwd=repo, check=True, stdout=subprocess.DEVNULL)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=repo, capture_output=True, text=True,
    )


def test_hook_allows_env_example(tmp_path):
    r = _run_with_staged(tmp_path, [".env.example"])
    assert r.returncode == 0, f"stderr: {r.stderr}"


def test_hook_allows_env_ci(tmp_path):
    r = _run_with_staged(tmp_path, [".env.ci"])
    assert r.returncode == 0, f"stderr: {r.stderr}"


def test_hook_allows_normal_files(tmp_path):
    r = _run_with_staged(tmp_path, ["README.md", "app/main.py", "data/test.db"])
    assert r.returncode == 0


def test_hook_blocks_dotenv(tmp_path):
    r = _run_with_staged(tmp_path, [".env"])
    assert r.returncode == 1
    assert ".env" in r.stderr
    assert "BLOCKED" in r.stderr


def test_hook_blocks_dotenv_local(tmp_path):
    r = _run_with_staged(tmp_path, [".env.local"])
    assert r.returncode == 1
    assert ".env.local" in r.stderr


def test_hook_blocks_dotenv_production(tmp_path):
    r = _run_with_staged(tmp_path, [".env.production"])
    assert r.returncode == 1


def test_hook_blocks_nested_dotenv(tmp_path):
    r = _run_with_staged(tmp_path, ["subdir/.env"])
    assert r.returncode == 1


def test_hook_message_includes_unblock_instructions(tmp_path):
    r = _run_with_staged(tmp_path, [".env"])
    assert "git reset HEAD" in r.stderr
    assert ".env.example" in r.stderr
