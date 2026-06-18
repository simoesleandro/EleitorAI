from typing import Optional

from core.db import get_db
from core.rag.embeddings import buscar_similares


def buscar(query: str, entidade_tipo: Optional[str] = None, k: int = 5) -> list[dict]:
    semantico = buscar_similares(query, entidade_tipo=entidade_tipo, k=k * 2)

    keyword = _buscar_keyword(query, entidade_tipo, k * 2)

    combinado = {}
    for r in semantico:
        key = (r["entidade_tipo"], r["entidade_id"])
        combinado[key] = {**r, "score_semantico": 1.0 / (1.0 + r.get("distancia", 1.0)), "score_keyword": 0.0}
    for r in keyword:
        key = (r["entidade_tipo"], r["entidade_id"])
        if key in combinado:
            combinado[key]["score_keyword"] = 1.0
        else:
            combinado[key] = {**r, "score_semantico": 0.0, "score_keyword": 1.0}

    for v in combinado.values():
        v["score_total"] = v["score_semantico"] + v["score_keyword"]

    ordenados = sorted(combinado.values(), key=lambda x: x["score_total"], reverse=True)
    return ordenados[:k]


def _buscar_keyword(query: str, entidade_tipo: Optional[str], limit: int) -> list[dict]:
    conn = get_db()
    try:
        termos = query.split()
        if not termos:
            return []
        where_clauses = " OR ".join(["conteudo LIKE ?"] * len(termos))
        params = [f"%{t}%" for t in termos]
        sql = f"SELECT entidade_tipo, entidade_id, conteudo FROM embeddings WHERE {where_clauses}"
        if entidade_tipo:
            sql += " AND entidade_tipo = ?"
            params.append(entidade_tipo)
        sql += " LIMIT ?"
        params.append(limit)
        cursor = conn.execute(sql, params)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
