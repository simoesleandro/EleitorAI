import logging

import httpx

from core.config import get_settings

logger = logging.getLogger(__name__)
TRANSPARENCIA_BASE = "https://api.portaldatransparencia.gov.br/api"


def buscar_transparencia(query: str, k: int = 5) -> list[dict]:
    resultados = []
    try:
        resultados.append({"fonte": "Portal Transparencia", "dados": _query_despesas(query)})
    except Exception as e:
        logger.warning(f"Portal Transparencia despesas falhou: {e}")
    return resultados[:k]


def _query_despesas(query: str) -> dict:
    api_key = get_settings().portal_transparencia_api_key
    headers = {"chave-api-dados": api_key} if api_key else {}
    resp = httpx.get(
        f"{TRANSPARENCIA_BASE}/despesas/v2",
        params={"q": query},
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
