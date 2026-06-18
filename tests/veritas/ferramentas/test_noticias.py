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


def test_buscar_noticias_retorna_apenas_matches():
    matching_entries = [
        MagicMock(title="economia cresce", link="https://exemplo.com/1", published="2026-06-18", summary="resumo 1"),
        MagicMock(title="esporte vence", link="https://exemplo.com/2", published="2026-06-18", summary="resumo 2"),
        MagicMock(title="mercado", link="https://exemplo.com/3", published="2026-06-18", summary="economia em alta"),
    ]
    empty_feed = MagicMock()
    empty_feed.entries = []
    with patch("veritas.ferramentas.noticias.feedparser.parse",
               side_effect=[MagicMock(entries=matching_entries)] + [empty_feed] * 10):
        results = buscar_noticias("economia", k=5)
    assert isinstance(results, list)
    assert len(results) == 2
    titulos = [r["titulo"] for r in results]
    assert "economia cresce" in titulos
    assert "mercado" in titulos
    assert "esporte vence" not in titulos


def test_buscar_noticias_filtra_por_query_ignorada_anteriormente():
    fake_feed = MagicMock()
    fake_feed.entries = [
        MagicMock(title="esporte", link="https://exemplo.com/1", published="2026-06-18", summary="futebol"),
        MagicMock(title="politica", link="https://exemplo.com/2", published="2026-06-18", summary="governo"),
    ]
    fake_feed.bozo = False
    with patch("veritas.ferramentas.noticias.feedparser.parse", return_value=fake_feed):
        results = buscar_noticias("xyz_nao_existe", k=5)
    assert results == []
