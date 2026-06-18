from unittest.mock import patch
from veritas.scrapers.checamos import scraper_checamos, parse_checamos_page
from core.modelos import FactCheck


FIXTURE_HTML = """
<article class="node--type-fact-check">
  <h2 class="node__title"><a href="/checamos/2026/06/18/afp-brasil-001">Afirmação checada</a></h2>
  <div class="field-name-field-verdict"><div class="field-item">Falso</div></div>
  <time datetime="2026-06-18">18 jun 2026</time>
  <div class="field-name-body"><p>Resumo da checagem</p></div>
  <div class="field-name-field-explanation"><p>Explicação detalhada da análise</p></div>
  <ul class="field-name-field-sources"><li>Fonte A</li><li>Fonte B</li></ul>
</article>
"""


def test_parse_checamos_page_extrai_factcheck():
    facts = parse_checamos_page(FIXTURE_HTML, base_url="https://checamos.afp.com")
    assert len(facts) == 1
    fc = facts[0]
    assert isinstance(fc, FactCheck)
    assert fc.veiculo == "Checamos"
    assert fc.titulo == "Afirmação checada"
    assert fc.veredito_original.lower() == "falso"
    assert fc.url == "https://checamos.afp.com/checamos/2026/06/18/afp-brasil-001"
    assert "Fonte A" in fc.fontes_agencia


def test_scraper_checamos_agrupa_multiplas_paginas(monkeypatch):
    pages = [
        ("https://checamos.afp.com/list?page=1", FIXTURE_HTML),
        ("https://checamos.afp.com/list?page=2", FIXTURE_HTML),
        ("https://checamos.afp.com/list?page=3", ""),
    ]
    def fake_fetch(url):
        for u, html in pages:
            if u == url:
                return html
        return ""
    with patch("veritas.scrapers.checamos.fetch", side_effect=fake_fetch):
        facts = scraper_checamos(max_pages=5)
    assert len(facts) == 2
