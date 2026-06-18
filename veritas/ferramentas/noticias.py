import logging

import feedparser

logger = logging.getLogger(__name__)
FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://www.estadao.com.br/rss/ultimas.xml",
    "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://www.cnnbrasil.com.br/rss/feed.xml",
]


def buscar_noticias(query: str, k: int = 5) -> list[dict]:
    resultados = []
    query_lower = query.lower()
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logger.warning(f"Noticias feed {feed_url} falhou: {e}")
            continue
        for entry in feed.entries[: k * 2]:
            titulo = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "")
            if query_lower in titulo.lower() or query_lower in summary.lower():
                resultados.append({
                    "fonte": "Noticias",
                    "titulo": titulo,
                    "url": getattr(entry, "link", ""),
                    "data": getattr(entry, "published", ""),
                    "resumo": summary,
                })
                if len(resultados) >= k:
                    return resultados
    return resultados


def _parse_feed(url: str) -> list[dict]:
    feed = feedparser.parse(url)
    itens = []
    for entry in feed.entries:
        itens.append({
            "titulo": getattr(entry, "title", ""),
            "link": getattr(entry, "link", ""),
            "publicado": getattr(entry, "published", ""),
            "resumo": getattr(entry, "summary", ""),
        })
    return itens
