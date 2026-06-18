import hashlib
import json
import logging
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi

from core.db import get_db
from core.modelos import Mencao

logger = logging.getLogger(__name__)


def coletar_transcricao(video_id: str, candidato_id: Optional[int] = None) -> list[Mencao]:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["pt", "pt-BR"])
    except Exception as e:
        logger.warning(f"sem legenda em {video_id}, fallback yt-dlp+whisper: {e}")
        return _fallback_whisper(video_id, candidato_id)

    mencoes = []
    for chunk in transcript:
        texto = chunk["text"].strip()
        if not texto:
            continue
        mencoes.append(
            Mencao(
                fonte_id=_ensure_fonte_youtube(video_id),
                candidato_id=candidato_id,
                texto=texto,
                timestamp=f"yt:{video_id}:{chunk['start']}",
                url=f"https://youtube.com/watch?v={video_id}&t={int(chunk['start'])}",
                metricas={"start": chunk["start"], "duration": chunk.get("duration", 0)},
                hash_conteudo=_hash_conteudo(video_id, texto),
            )
        )
    return mencoes


def _fallback_whisper(video_id: str, candidato_id: Optional[int]) -> list[Mencao]:
    return []


def coletar_comentarios(video_id: str, candidato_id: Optional[int] = None) -> list[Mencao]:
    return []


def salvar_mencao(mencao: Mencao) -> int:
    conn = get_db()
    try:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO mencoes
            (fonte_id, candidato_id, texto, autor, autor_id, timestamp, url, metricas, hash_conteudo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mencao.fonte_id, mencao.candidato_id, mencao.texto,
                mencao.autor, mencao.autor_id, mencao.timestamp,
                mencao.url, _dump_metricas(mencao.metricas), mencao.hash_conteudo,
            ),
        )
        conn.commit()
        if cursor.lastrowid and cursor.lastrowid > 0:
            return cursor.lastrowid
        row = conn.execute(
            "SELECT id FROM mencoes WHERE hash_conteudo=?", (mencao.hash_conteudo,)
        ).fetchone()
        return row["id"] if row else 0
    finally:
        conn.close()


def _ensure_fonte_youtube(video_id: str) -> int:
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO fontes (tipo, identificador, coletor) VALUES ('youtube', ?, ?)",
            (video_id, "core.coletores.youtube"),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id FROM fontes WHERE tipo='youtube' AND identificador=?", (video_id,)
        ).fetchone()
        return row["id"]
    finally:
        conn.close()


def _hash_conteudo(fonte_id: str, texto: str) -> str:
    return hashlib.sha256(f"{fonte_id}|{texto}".encode("utf-8")).hexdigest()


def _dump_metricas(metricas: dict) -> str:
    return json.dumps(metricas, ensure_ascii=False)
