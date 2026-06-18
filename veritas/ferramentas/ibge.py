import logging

import httpx


logger = logging.getLogger(__name__)
IBGE_BASE = "https://servicodados.ibge.gov.br/api/v1"


def buscar_ibge(query: str, k: int = 5) -> list[dict]:
    resultados = []
    try:
        resultados.append({"fonte": "IBGE populacao", "dados": _query_populacao()})
    except Exception as e:
        logger.warning(f"IBGE populacao falhou: {e}")
    try:
        resultados.append({"fonte": "IBGE agregados", "dados": _query_agregados(query)})
    except Exception as e:
        logger.warning(f"IBGE agregados falhou: {e}")
    return resultados[:k]


def _query_populacao() -> dict:
    resp = httpx.get(f"{IBGE_BASE}/projecoes/populacao", timeout=15)
    resp.raise_for_status()
    return resp.json()


def _query_agregados(query: str) -> dict:
    resp = httpx.get(
        "https://servicodados.ibge.gov.br/api/v3/agregados",
        params={"pesquisa": query},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
