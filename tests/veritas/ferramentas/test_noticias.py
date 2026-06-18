from unittest.mock import MagicMock, patch

from veritas.ferramentas.noticias import buscar_noticias, _parse_feed


def test_parse_feed_retorna_lista():
    fake_feed = MagicMock()
    fake_feed.entries = [
        MagicMock(title="titulo 1", link="https://exemplo.com/1", published="2026-06-18", summary="resumo 1"),
        MagicMock(title="titulo 2", link="https://exemplo.com/2", published="2026-06-18", summary="resumo 2"),
    ]
    fake_feed.bozo = False
    with patch("veritas.ferramentas.noticias.feedparser.parse", return_value=fake_feed):
        result = _parse_feed("https://exemplo.com/feed")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["titulo"] == "titulo 1"


def test_buscar_noticias_retorna_lista():
    fake_feed = MagicMock()
    fake_feed.entries = [
        MagicMock(title="titulo 1", link="https://exemplo.com/1", published="2026-06-18", summary="resumo 1"),
    ]
    fake_feed.bozo = False
    with patch("veritas.ferramentas.noticias.feedparser.parse", return_value=fake_feed):
        results = buscar_noticias("test query")
    assert isinstance(results, list)
    assert len(results) >= 1
