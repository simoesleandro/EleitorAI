from unittest.mock import patch
from veritas.scrapers.estadao_verifica import scraper_estadao_verifica, parse_estadao_verifica_page
from core.modelos import FactCheck


FIXTURE_HTML = """
<article class="post">
  <h2 class="entry-title"><a href="/blogs/estadao-verifica/checagem-exemplo-123">Checagem de exemplo</a></h2>
  <span class="verdict">Falso</span>
  <time datetime="2026-06-18">18/06/2026</time>
  <div class="entry-summary"><p>Resumo da checagem em parágrafo</p></div>
  <div class="entry-content"><p>Explicação completa da análise</p></div>
  <ul class="fontes"><li>TSE</li><li>Diário Oficial</li></ul>
</article>
"""


def test_parse_estadao_verifica_page_extrai_factcheck():
    facts = parse_estadao_verifica_page(FIXTURE_HTML, base_url="https://politica.estadao.com.br")
    assert len(facts) == 1
    fc = facts[0]
    assert isinstance(fc, FactCheck)
    assert fc.veiculo == "Estadao Verifica"
    assert fc.titulo == "Checagem de exemplo"
    assert fc.veredito_original.lower() == "falso"
    assert fc.url == "https://politica.estadao.com.br/blogs/estadao-verifica/checagem-exemplo-123"
    assert "TSE" in fc.fontes_agencia


def test_scraper_estadao_verifica_agrupa_multiplas_paginas(monkeypatch):
    pages = [
        ("https://politica.estadao.com.br/blogs/estadao-verifica/page/1", FIXTURE_HTML),
        ("https://politica.estadao.com.br/blogs/estadao-verifica/page/2", FIXTURE_HTML),
        ("https://politica.estadao.com.br/blogs/estadao-verifica/page/3", ""),
    ]
    def fake_fetch(url):
        for u, html in pages:
            if u == url:
                return html
        return ""
    with patch("veritas.scrapers.estadao_verifica.fetch", side_effect=fake_fetch):
        facts = scraper_estadao_verifica(max_pages=5)
    assert len(facts) == 2
