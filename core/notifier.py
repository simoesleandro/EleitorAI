import json
import logging
from typing import Optional

import httpx

from core.config import get_settings
from core.modelos import Alerta

logger = logging.getLogger(__name__)


def enviar_telegram(mensagem: str, chat_id: Optional[str] = None, parse_mode: str = "Markdown") -> bool:
    settings = get_settings()
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN nao configurado, pulando envio")
        return False
    target_chat = chat_id or settings.telegram_chat_id
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        resp = httpx.post(
            url,
            json={"chat_id": target_chat, "text": mensagem, "parse_mode": parse_mode},
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("ok") is True
    except Exception as e:
        logger.error(f"erro enviando telegram: {e}")
        return False


def enviar_alerta(alerta: Alerta) -> bool:
    severidade_emoji = {
        "info": "[INFO]",
        "medio": "[MEDIO]",
        "alto": "[ALTO]",
        "critico": "[CRITICO]",
    }
    emoji = severidade_emoji.get(alerta.severidade, "[ALERTA]")
    texto = (
        f"*{emoji} {alerta.titulo}*\n"
        f"_Modulo: {alerta.modulo}_\n\n"
        f"{json.dumps(alerta.payload, ensure_ascii=False, indent=2)}"
    )
    return enviar_telegram(texto)
