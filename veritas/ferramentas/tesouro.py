import logging

import httpx

logger = logging.getLogger(__name__)
TESOURO_BASE = "https://apidatalake.tesouro.gov.br/ords/siconfi/v2"


def buscar_tesouro(query: str, k: int = 5) -> list[dict]:
    resultados = []
    try:
        resultados.append({"fonte": "Tesouro Nacional", "dados": _query_receitas(query)})
    except Exception as e:
        logger.warning(f"Tesouro receitas falhou: {e}")
    return resultados[:k]


def _query_receitas(query: str) -> dict:
    resp = httpx.get(
        f"{TESOURO_BASE}/ente/{query}/receitas",
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
