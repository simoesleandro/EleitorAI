from unittest.mock import patch
from veritas.scrapers.lupa import scraper_lupa, parse_lupa_page
from core.modelos import FactCheck


FIXTURE_HTML = """
<article class="fact-check">
  <h2><a href="/checagem/123/crescimento-zero">Crescimento populacional zero</a></h2>
  <span class="verdict">Falso</span>
  <time datetime="2026-06-18">18/06/2026</time>
  <p class="claim">Candidato afirmou zero crescimento em 10 anos</p>
  <p class="explanation">IBGE aponta crescimento de 8.2% no Censo 2022</p>
  <ul class="sources"><li>IBGE</li><li>Censo 2022</li></ul>
</article>
"""


def test_parse_lupa_page_extrai_factcheck():
    facts = parse_lupa_page(FIXTURE_HTML, base_url="https://agencialupa.com.br")
    assert len(facts) == 1
    fc = facts[0]
    assert isinstance(fc, FactCheck)
    assert fc.veiculo == "Lupa"
    assert fc.titulo == "Crescimento populacional zero"
    assert fc.veredito_original.lower() == "falso"
    assert fc.url == "https://agencialupa.com.br/checagem/123/crescimento-zero"
    assert "IBGE" in fc.fontes_agencia


def test_scraper_lupa_agrupa_multiplas_paginas(monkeypatch):
    pages = [
        ("https://agencialupa.com.br/page/1", FIXTURE_HTML),
        ("https://agencialupa.com.br/page/2", FIXTURE_HTML),
        ("https://agencialupa.com.br/page/3", ""),
    ]
    def fake_fetch(url):
        for u, html in pages:
            if u == url:
                return html
        return ""
    with patch("veritas.scrapers.lupa.fetch", side_effect=fake_fetch):
        facts = scraper_lupa(max_pages=5)
    assert len(facts) == 2
