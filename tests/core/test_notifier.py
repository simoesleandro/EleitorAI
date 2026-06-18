import json
from core.notifier import enviar_telegram, enviar_alerta
from core.modelos import Alerta


def test_enviar_telegram_success(monkeypatch, respx_mock):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    respx_mock.post("https://api.telegram.org/bottest-token/sendMessage").respond(200, json={"ok": True})
    ok = enviar_telegram("hello world")
    assert ok is True


def test_enviar_telegram_failure(monkeypatch, respx_mock):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    respx_mock.post("https://api.telegram.org/bottest-token/sendMessage").respond(500)
    ok = enviar_telegram("hello")
    assert ok is False


def test_enviar_alerta_formata_markdown(monkeypatch, respx_mock):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    route = respx_mock.post("https://api.telegram.org/bottest-token/sendMessage").respond(200, json={"ok": True})
    alerta = Alerta(
        modulo="veritas",
        severidade="alto",
        titulo="Claim falsa detectada",
        payload={"candidato": "X", "veredito": "falso"},
    )
    ok = enviar_alerta(alerta)
    assert ok is True
    body = json.loads(route.calls[0].request.content)
    assert "Claim falsa detectada" in body["text"]
    assert "ALTO" in body["text"]
