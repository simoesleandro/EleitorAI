import logging
import pytest
from core.logging_redactor import SecretRedactingFilter, install_redactor, REDACTED, uninstall_redactor


def _make_record(msg: str, args=()):
    return logging.LogRecord("test", logging.INFO, "path", 1, msg, args, None)


def test_redact_exact_value():
    flt = SecretRedactingFilter(secrets=["my-secret-key-12345"])
    rec = _make_record("token is my-secret-key-12345 in log")
    assert flt.filter(rec)
    assert "my-secret-key-12345" not in rec.msg
    assert REDACTED in rec.msg


def test_redact_multiple_secrets():
    flt = SecretRedactingFilter(secrets=["secret-aaa", "secret-bbb"])
    rec = _make_record("values: secret-aaa and secret-bbb and public")
    flt.filter(rec)
    assert "secret-aaa" not in rec.msg
    assert "secret-bbb" not in rec.msg
    assert "public" in rec.msg


def test_short_value_ignored():
    flt = SecretRedactingFilter(secrets=["ab"])
    rec = _make_record("value is ab")
    flt.filter(rec)
    assert rec.msg == "value is ab"


def test_update_secrets():
    flt = SecretRedactingFilter(secrets=["old-secret-key-12345"])
    rec = _make_record("new is new-secret-key-67890 in log")
    flt.filter(rec)
    assert "new-secret-key-67890" in rec.msg
    flt.update_secrets(["new-secret-key-67890"])
    rec = _make_record("new is new-secret-key-67890 in log")
    flt.filter(rec)
    assert "new-secret-key-67890" not in rec.msg


def test_redact_key_value_pattern_key_eq():
    flt = SecretRedactingFilter(secrets=[])
    rec = _make_record("GEMINI_API_KEY=abc123def456ghi789")
    flt.filter(rec)
    assert "abc123def456ghi789" not in rec.msg
    assert REDACTED in rec.msg


def test_redact_key_value_pattern_key_colon():
    flt = SecretRedactingFilter(secrets=[])
    rec = _make_record("TELEGRAM_BOT_TOKEN: 123456:ABC-DEF")
    flt.filter(rec)
    assert "123456:ABC-DEF" not in rec.msg
    assert REDACTED in rec.msg


def test_redact_key_value_lowercase():
    flt = SecretRedactingFilter(secrets=[])
    rec = _make_record("admin_password=supersecret123")
    flt.filter(rec)
    assert "supersecret123" not in rec.msg
    assert REDACTED in rec.msg


def test_redact_args_tuple():
    flt = SecretRedactingFilter(secrets=["my-token-xyz12345"])
    rec = _make_record("token is %s", ("my-token-xyz12345",))
    flt.filter(rec)
    assert "my-token-xyz12345" not in rec.args[0]
    assert REDACTED in rec.args[0]


def test_redact_args_dict():
    flt = SecretRedactingFilter(secrets=["another-secret-999"])
    rec = _make_record("payload: %(k)s", ({"k": "another-secret-999"},))
    flt.filter(rec)
    assert "another-secret-999" not in rec.args["k"]
    assert REDACTED in rec.args["k"]


def test_non_string_msg_passes():
    flt = SecretRedactingFilter(secrets=["x" * 20])
    rec = _make_record(12345)
    assert flt.filter(rec)
    assert rec.msg == 12345


def test_install_redactor_returns_filter():
    flt = install_redactor()
    assert isinstance(flt, SecretRedactingFilter)
    uninstall_redactor()


def test_install_redactor_idempotent():
    flt1 = install_redactor()
    flt2 = install_redactor()
    assert flt1 is flt2
    uninstall_redactor()


def test_install_redactor_picks_up_settings_secrets(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTestSecretKey12345XYZ")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "9999999:TestTokenSecretABCDE")
    from core.config import get_settings
    get_settings.cache_clear()
    flt = install_redactor()
    rec = _make_record("using AIzaSyTestSecretKey12345XYZ and 9999999:TestTokenSecretABCDE")
    flt.filter(rec)
    assert "AIzaSyTestSecretKey12345XYZ" not in rec.msg
    assert "9999999:TestTokenSecretABCDE" not in rec.msg
    uninstall_redactor()
    get_settings.cache_clear()


def test_no_secret_passes_through():
    flt = SecretRedactingFilter(secrets=[])
    rec = _make_record("normal log message with no secrets")
    flt.filter(rec)
    assert rec.msg == "normal log message with no secrets"
