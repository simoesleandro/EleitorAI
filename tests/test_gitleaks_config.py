"""Tests for the gitleaks configuration and pre-commit integration."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GITLEAKS_TOML = ROOT / ".gitleaks.toml"


def test_gitleaks_config_exists():
    assert GITLEAKS_TOML.exists(), ".gitleaks.toml must exist"


def test_gitleaks_config_has_title():
    content = GITLEAKS_TOML.read_text(encoding="utf-8")
    assert "title" in content
    assert "EleitorAI" in content


def test_gitleaks_config_extends_defaults():
    content = GITLEAKS_TOML.read_text(encoding="utf-8")
    assert "useDefault" in content, "Must inherit gitleaks default rules"


def test_gitleaks_allowlist_includes_fixtures():
    content = GITLEAKS_TOML.read_text(encoding="utf-8")
    for fragment in (r"\.env\.ci", r"\.env\.example", r"tests/", r"docs/", "README"):
        assert fragment in content, f"Allowlist should reference {fragment}"


def test_gitleaks_config_has_custom_rules():
    content = GITLEAKS_TOML.read_text(encoding="utf-8")
    for rule in ("eleitorai-gemini-key", "eleitorai-telegram-bot-token",
                 "eleitorai-telegram-api-hash", "eleitorai-langfuse-key"):
        assert rule in content, f"Custom rule {rule} missing"


def test_gitleaks_toml_is_valid_toml(tmp_path):
    """Parse the TOML to catch syntax errors early."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            pytest.skip("tomllib/tomli not available")
    with open(GITLEAKS_TOML, "rb") as f:
        data = tomllib.load(f)
    assert "title" in data
    assert "extend" in data
    assert data["extend"]["useDefault"] is True
    assert "allowlist" in data
    assert "rules" in data
    assert len(data["rules"]) >= 4


def test_precommit_config_references_gitleaks():
    pc = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "gitleaks" in pc.lower()


def test_precommit_config_references_env_blocker():
    pc = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "check_no_env.py" in pc
    assert "block-env-files" in pc


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks not installed")
def test_gitleaks_scans_fixtures_cleanly(tmp_path):
    """If gitleaks is installed, run it against the repo to verify config works.

    This is an integration test; the gitleaks binary is not required to pass
    the suite (see skipif).
    """
    result = subprocess.run(
        ["gitleaks", "detect", "--config", str(GITLEAKS_TOML),
         "--source", str(ROOT), "--no-banner", "--exit-code", "1"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        pytest.fail(
            f"gitleaks found secrets:\n{result.stdout}\n{result.stderr}"
        )
