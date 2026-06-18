import struct
from typing import Optional

from core.db import get_db
from core.llm import gerar_embedding


def indexar(entidade_tipo: str, entidade_id: int, conteudo: str) -> None:
    emb = gerar_embedding(conteudo)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO embeddings (entidade_tipo, entidade_id, conteudo, embedding) VALUES (?, ?, ?, ?)",
            (entidade_tipo, entidade_id, conteudo, _to_blob(emb)),
        )
        conn.commit()
    finally:
        conn.close()


def buscar_similares(
    query: str,
    entidade_tipo: Optional[str] = None,
    k: int = 5,
) -> list[dict]:
    query_emb = gerar_embedding(query)
    conn = get_db()
    try:
        if entidade_tipo:
            sql = (
                "SELECT entidade_tipo, entidade_id, conteudo, distance AS distancia "
                "FROM embeddings WHERE embedding MATCH ? "
                "AND entidade_tipo = ? ORDER BY distance LIMIT ?"
            )
            cursor = conn.execute(sql, (_to_blob(query_emb), entidade_tipo, k))
        else:
            sql = (
                "SELECT entidade_tipo, entidade_id, conteudo, distance AS distancia "
                "FROM embeddings WHERE embedding MATCH ? "
                "ORDER BY distance LIMIT ?"
            )
            cursor = conn.execute(sql, (_to_blob(query_emb), k))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def remover(entidade_tipo: str, entidade_id: int) -> None:
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM embeddings WHERE entidade_tipo=? AND entidade_id=?",
            (entidade_tipo, entidade_id),
        )
        conn.commit()
    finally:
        conn.close()


def _to_blob(values: list[float]) -> bytes:
    return struct.pack(f"{len(values)}f", *values)
