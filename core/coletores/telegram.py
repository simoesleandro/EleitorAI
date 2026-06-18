import asyncio
import hashlib
import logging

from telethon import TelegramClient
from telethon.tl.types import Message

from core.config import get_settings
from core.db import get_db
from core.modelos import Mencao

logger = logging.getLogger(__name__)


def coletar_canal(canal: str, limite: int = 100) -> list[Mencao]:
    return asyncio.run(_coletar_canal_async(canal, limite))


async def _coletar_canal_async(canal: str, limite: int) -> list[Mencao]:
    settings = get_settings()
    client = TelegramClient("eleitorai_session", settings.telegram_api_id, settings.telegram_api_hash)
    await client.start()
    try:
        fonte_id = _ensure_fonte_telegram(canal)
        mencoes = []
        async for msg in client.iter_messages(canal, limit=limite):
            if not msg.text:
                continue
            mencoes.append(_to_mencao(msg, fonte_id))
        return mencoes
    finally:
        await client.disconnect()


def _to_mencao(msg: Message, fonte_id: int) -> Mencao:
    metricas = {}
    if msg.fwd_from and msg.fwd_from.from_id:
        fwd_id = getattr(msg.fwd_from.from_id, "channel_id", None) or getattr(msg.fwd_from.from_id, "user_id", None)
        metricas["forwarded_from"] = fwd_id

    sender_username = None
    if msg.sender:
        sender_username = getattr(msg.sender, "username", None) or str(msg.sender_id)

    return Mencao(
        fonte_id=fonte_id,
        texto=msg.text,
        autor=sender_username,
        autor_id=str(msg.sender_id),
        timestamp=msg.date.isoformat(),
        metricas=metricas,
        hash_conteudo=_hash_conteudo(fonte_id, msg.id, msg.text),
    )


def _ensure_fonte_telegram(canal: str) -> int:
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO fontes (tipo, identificador, coletor) VALUES ('telegram', ?, ?)",
            (canal, "core.coletores.telegram"),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id FROM fontes WHERE tipo='telegram' AND identificador=?", (canal,)
        ).fetchone()
        return row["id"]
    finally:
        conn.close()


def _hash_conteudo(fonte_id: int, msg_id: int, texto: str) -> str:
    return hashlib.sha256(f"tg:{fonte_id}|{msg_id}|{texto}".encode("utf-8")).hexdigest()
