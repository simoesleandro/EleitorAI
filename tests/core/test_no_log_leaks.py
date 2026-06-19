"""Meta-test: validates that no test logs expose secret values.

This test simulates a sensitive environment with realistic-looking fake
secrets, triggers a few log-emitting code paths, and verifies the
SecretRedactingFilter scrubs them from log output.

If this test ever fails, it means a test (or production code path)
is leaking credentials into log output. Treat as a security regression.
"""
import logging
import os

import pytest

from core.logging_redactor import (
    SecretRedactingFilter,
    install_redactor,
    uninstall_redactor,
    REDACTED,
)

FAKE_GEMINI = "AIzaSyFakeTESTKey1234567890abcdef"
FAKE_TG_BOT = "1234567890:AAFakeTestBotTokenSecretABCDEFG"
FAKE_TG_API = "f0ed1f38fakehashnotreal1234567890"
FAKE_ADMIN = "FakeAdminPasswordXYZ2026"
FAKE_SECRET = "FakeFlaskSecretKeyHexabc123def456"


@pytest.fixture
def fake_secrets(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", FAKE_GEMINI)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", FAKE_TG_BOT)
    monkeypatch.setenv("TELEGRAM_API_HASH", FAKE_TG_API)
    monkeypatch.setenv("ADMIN_PASS", FAKE_ADMIN)
    monkeypatch.setenv("SECRET_KEY", FAKE_SECRET)
    from core.config import get_settings
    get_settings.cache_clear()
    install_redactor()
    yield
    uninstall_redactor()
    get_settings.cache_clear()


def test_fake_secrets_never_appear_in_log_output(fake_secrets, caplog):
    for secret in (FAKE_GEMINI, FAKE_TG_BOT, FAKE_TG_API, FAKE_ADMIN, FAKE_SECRET):
        with caplog.at_level(logging.INFO):
            logging.getLogger("meta_test").info(
                "simulated leak: %s embedded in payload", secret
            )
    output = caplog.text
    for secret in (FAKE_GEMINI, FAKE_TG_BOT, FAKE_TG_API, FAKE_ADMIN, FAKE_SECRET):
        assert secret not in output, (
            f"Secret leaked into log output: {secret[:8]}..."
        )
    assert REDACTED in output


def test_fake_secrets_redacted_in_key_value_pattern(fake_secrets, caplog):
    with caplog.at_level(logging.INFO):
        logging.getLogger("meta_test").info(
            "config: GEMINI_API_KEY=%s TELEGRAM_BOT_TOKEN=%s",
            FAKE_GEMINI, FAKE_TG_BOT,
        )
        logging.getLogger("meta_test").info(
            "raw: GEMINI_API_KEY=%s and another KEY=LEAKED12345XYZ",
            FAKE_GEMINI,
        )
    output = caplog.text
    assert FAKE_GEMINI not in output
    assert FAKE_TG_BOT not in output
    assert REDACTED in output


def test_safe_log_messages_pass_through(fake_secrets, caplog):
    with caplog.at_level(logging.INFO):
        logging.getLogger("meta_test").info("processing 5 mentions from @channel_public")
        logging.getLogger("meta_test").info("job complete: status=ok")
    output = caplog.text
    assert "processing 5 mentions from @channel_public" in output
    assert "job complete: status=ok" in output


def test_redactor_covers_child_loggers_via_factory(fake_secrets, caplog):
    """Critical: child loggers must also have secrets redacted.

    The factory approach ensures all loggers (not just root) get redacted.
    """
    with caplog.at_level(logging.INFO):
        logging.getLogger("veritas.agentes.extrator").info("using key %s", FAKE_GEMINI)
        logging.getLogger("eco.pipeline").info("config %s", FAKE_TG_BOT)
        logging.getLogger("worker.jobs_eco").info("api %s", FAKE_TG_API)
    output = caplog.text
    for s in (FAKE_GEMINI, FAKE_TG_BOT, FAKE_TG_API):
        assert s not in output
