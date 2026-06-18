import logging
from typing import Callable, Optional

from core.rag.embeddings import indexar
from veritas.scrapers.lupa import scraper_lupa
from veritas.scrapers.boatos import scraper_boatos
from veritas.scrapers.fato_fake import scraper_fato_fake
from veritas.scrapers.checamos import scraper_checamos
from veritas.scrapers.estadao_verifica import scraper_estadao_verifica

logger = logging.getLogger(__name__)

SCRAPERS = {
    "Lupa": "scraper_lupa",
    "Boatos": "scraper_boatos",
    "FatoFake": "scraper_fato_fake",
    "Checamos": "scraper_checamos",
    "EstadaoVerifica": "scraper_estadao_verifica",
}


def seed_base_fatos(progress_callback: Optional[Callable] = None) -> dict:
    por_veiculo = {}
    total = 0
    for nome, scraper_name in SCRAPERS.items():
        scraper = globals()[scraper_name]
        try:
            facts = scraper()
        except Exception as e:
            logger.error(f"scraper {nome} falhou: {e}")
            facts = []
        por_veiculo[nome] = len(facts)
        for fc in facts:
            conteudo = f"{fc.claim_checada}\n{fc.explicacao}\nVeredito: {fc.veredito_original}"
            indexar("factcheck", hash(fc.url) & 0x7FFFFFFF, conteudo)
            total += 1
            if progress_callback:
                progress_callback(nome, total)
    return {"total": total, "por_veiculo": por_veiculo}
