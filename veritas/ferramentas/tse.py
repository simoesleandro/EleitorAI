import logging

import httpx

logger = logging.getLogger(__name__)
TSE_BASE = "https://dadosabertos.tse.jus.br"


def buscar_tse(query: str, k: int = 5) -> list[dict]:
    resultados = []
    try:
        resultados.append({"fonte": "TSE", "dados": _query_candidatos(query)})
    except Exception as e:
        logger.warning(f"TSE candidatos falhou: {e}")
    return resultados[:k]


def _query_candidatos(query: str) -> dict:
    resp = httpx.get(
        f"{TSE_BASE}/api/v2/candidatos",
        params={"uf": query},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
