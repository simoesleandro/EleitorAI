import logging

import httpx

logger = logging.getLogger(__name__)
DATASUS_BASE = "http://tabnet.datasus.gov.br"


def buscar_datasus(query: str, k: int = 5) -> list[dict]:
    resultados = []
    try:
        resultados.append({"fonte": "DataSUS", "dados": _query_mortalidade(query)})
    except Exception as e:
        logger.warning(f"DataSUS mortalidade falhou: {e}")
    return resultados[:k]


def _query_mortalidade(query: str) -> dict:
    resp = httpx.get(
        f"{DATASUS_BASE}/cnv/obt10uf",
        params={"uf": query},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
