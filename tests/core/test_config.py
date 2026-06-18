import os
from core.config import get_settings, Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    monkeypatch.setenv("TELEGRAM_API_ID", "11111")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash123")
    monkeypatch.setenv("ADMIN_PASS", "mypass")
    monkeypatch.setenv("SECRET_KEY", "secret")
    monkeypatch.setenv("DB_PATH", "data/test.db")

    settings = Settings()

    assert settings.gemini_api_key == "test-key"
    assert settings.telegram_bot_token == "test-token"
    assert settings.telegram_chat_id == "123456"
    assert settings.telegram_api_id == 11111
    assert settings.telegram_api_hash == "hash123"
    assert settings.admin_pass == "mypass"
    assert settings.secret_key == "secret"
    assert settings.db_path == "data/test.db"


def test_get_settings_returns_cached_instance(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
