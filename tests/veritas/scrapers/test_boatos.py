from unittest.mock import patch
from veritas.scrapers.boatos import scraper_boatos, parse_boatos_page
from core.modelos import FactCheck


FIXTURE_HTML = """
<article class="post">
  <h2><a href="/vacina-nao-funciona">Vacina não funciona</a></h2>
  <span class="classificacao">Falso</span>
  <time datetime="2026-06-17">17/06/2026</time>
  <p class="claim">Post afirma que vacinas não têm eficácia comprovada</p>
  <p class="explicacao">Estudos clínicos demonstram eficácia superior a 90% para a maioria dos imunizantes</p>
  <ul class="fontes"><li>Estudo Pfizer</li><li>OMS</li></ul>
</article>
"""


def test_parse_boatos_page_extrai_factcheck():
    facts = parse_boatos_page(FIXTURE_HTML, base_url="https://www.boatos.org")
    assert len(facts) == 1
    fc = facts[0]
    assert isinstance(fc, FactCheck)
    assert fc.veiculo == "Boatos"
    assert fc.titulo == "Vacina não funciona"
    assert fc.veredito_original.lower() == "falso"
    assert fc.url == "https://www.boatos.org/vacina-nao-funciona"
    assert "OMS" in fc.fontes_agencia


def test_scraper_boatos_agrupa_multiplas_paginas(monkeypatch):
    pages = [
        ("https://www.boatos.org/page/1", FIXTURE_HTML),
        ("https://www.boatos.org/page/2", FIXTURE_HTML),
        ("https://www.boatos.org/page/3", ""),
    ]
    def fake_fetch(url):
        for u, html in pages:
            if u == url:
                return html
        return ""
    with patch("veritas.scrapers.boatos.fetch", side_effect=fake_fetch):
        facts = scraper_boatos(max_pages=5)
    assert len(facts) == 2
