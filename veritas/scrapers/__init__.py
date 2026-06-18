import logging

import httpx

logger = logging.getLogger(__name__)


def fetch(url: str, timeout: int = 30) -> str:
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True)
        return resp.text if resp.status_code == 200 else ""
    except Exception as e:
        logger.warning(f"fetch {url} falhou: {e}")
        return ""
