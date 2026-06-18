from unittest.mock import patch
from veritas.scrapers.fato_fake import scraper_fato_fake, parse_fato_fake_page
from core.modelos import FactCheck


FIXTURE_HTML = """
<article class="feed-post">
  <h2 class="feed-post-link-title"><a href="/fato-ou-fake/2026/06/18/eleicoes-2026.ghtml">Título da checagem</a></h2>
  <span class="feed-post-header-chapeu">FATO OU FAKE</span>
  <time datetime="2026-06-18T10:00:00">18/06/2026</time>
  <p class="feed-post-body-resumo">Resumo do que foi checado</p>
  <div class="feed-post-body-explanation">Explicação detalhada da análise</div>
  <ul class="fontes"><li>Fonte 1</li><li>Fonte 2</li></ul>
</article>
"""


def test_parse_fato_fake_page_extrai_factcheck():
    facts = parse_fato_fake_page(FIXTURE_HTML, base_url="https://g1.globo.com")
    assert len(facts) == 1
    fc = facts[0]
    assert isinstance(fc, FactCheck)
    assert fc.veiculo == "Fato ou Fake"
    assert fc.titulo == "Título da checagem"
    assert fc.veredito_original == "FATO OU FAKE"
    assert fc.url == "https://g1.globo.com/fato-ou-fake/2026/06/18/eleicoes-2026.ghtml"
    assert "Fonte 1" in fc.fontes_agencia


def test_scraper_fato_fake_agrupa_multiplas_paginas(monkeypatch):
    pages = [
        ("https://g1.globo.com/fato-ou-fake/page/1", FIXTURE_HTML),
        ("https://g1.globo.com/fato-ou-fake/page/2", FIXTURE_HTML),
        ("https://g1.globo.com/fato-ou-fake/page/3", ""),
    ]
    def fake_fetch(url):
        for u, html in pages:
            if u == url:
                return html
        return ""
    with patch("veritas.scrapers.fato_fake.fetch", side_effect=fake_fetch):
        facts = scraper_fato_fake(max_pages=5)
    assert len(facts) == 2
