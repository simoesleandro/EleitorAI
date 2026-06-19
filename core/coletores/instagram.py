import hashlib
import logging

from core.db import get_db
from core.modelos import Mencao

logger = logging.getLogger(__name__)

BLOCK_RISK_WARNING = (
    "Instagram scraping e best-effort: ToS restritivo, blocks frequentes. "
    "Use Telegram + YouTube como fontes primarias."
)


def coletar_posts(handle: str, limite: int = 20) -> list[Mencao]:
    logger.warning(BLOCK_RISK_WARNING)
    try:
        page = _abrir_pagina(handle)
    except Exception as e:
        logger.warning(f"instagram bloqueado para {handle}: {e}")
        return []
    try:
        posts = page.query_selector_all("article")[:limite]
        mencoes = []
        fonte_id = _ensure_fonte_instagram(handle)
        for post in posts:
            try:
                texto_el = post.query_selector("h2 + div") or post.query_selector("div > span")
                texto = texto_el.text_content().strip() if texto_el else ""
                link_el = post.query_selector("a[href*='/p/']")
                url = link_el.get_attribute("href") if link_el else None
                if not texto:
                    continue
                mencoes.append(Mencao(
                    fonte_id=fonte_id,
                    texto=texto,
                    autor=handle,
                    timestamp="",
                    url=url,
                    hash_conteudo=_hash_conteudo(handle, texto),
                ))
            except Exception as e:
                logger.warning(f"erro parsing post: {e}")
                continue
        return mencoes
    finally:
        try:
            page.context.browser.close()
        except Exception:
            pass


def _abrir_pagina(handle: str):
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"https://instagram.com/{handle.lstrip('@')}/", timeout=20000)
    page.wait_for_selector("article", timeout=5000)
    return page


def _ensure_fonte_instagram(handle: str) -> int:
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO fontes (tipo, identificador, coletor) VALUES ('instagram', ?, ?)",
            (handle, "core.coletores.instagram"),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id FROM fontes WHERE tipo='instagram' AND identificador=?", (handle,)
        ).fetchone()
        return row["id"]
    finally:
        conn.close()


def _hash_conteudo(fonte: str, texto: str) -> str:
    return hashlib.sha256(f"ig:{fonte}|{texto}".encode("utf-8")).hexdigest()
