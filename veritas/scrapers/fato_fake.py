import logging
from bs4 import BeautifulSoup

from core.modelos import FactCheck
from veritas.scrapers import fetch

logger = logging.getLogger(__name__)
BASE_URL = "https://g1.globo.com"


def scraper_fato_fake(max_pages: int = 50) -> list[FactCheck]:
    all_facts = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/fato-ou-fake/page/{page}"
        html = fetch(url)
        if not html:
            break
        facts = parse_fato_fake_page(html, base_url=BASE_URL)
        if not facts:
            break
        all_facts.extend(facts)
    return all_facts


def parse_fato_fake_page(html: str, base_url: str) -> list[FactCheck]:
    soup = BeautifulSoup(html, "lxml")
    facts = []
    for article in soup.select("article.feed-post, article"):
        title_a = article.select_one(".feed-post-link-title a, h2 a, h3 a")
        if not title_a:
            continue
        href = title_a.get("href", "")
        url = href if href.startswith("http") else f"{base_url}{href}"
        title = title_a.get_text(strip=True)

        verdict_el = article.select_one(".feed-post-header-chapeu, .verdict, [class*=verdict]")
        verdict = verdict_el.get_text(strip=True) if verdict_el else ""

        time_el = article.select_one("time")
        data = time_el.get("datetime", "") if time_el else ""

        claim_el = article.select_one(".feed-post-body-resumo, .claim, .resumo")
        claim = claim_el.get_text(strip=True) if claim_el else title

        expl_el = article.select_one(".feed-post-body-explanation, .explicacao, .explanation, p")
        expl = expl_el.get_text(strip=True) if expl_el else ""

        sources = [li.get_text(strip=True) for li in article.select(".fontes li, .sources li")]

        facts.append(FactCheck(
            titulo=title, veiculo="Fato ou Fake", url=url, data=data,
            veredito_original=verdict, claim_checada=claim,
            explicacao=expl, fontes_agencia=sources,
        ))
    return facts
