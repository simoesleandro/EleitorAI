import pytest
from unittest.mock import patch, MagicMock
from core.coletores.instagram import coletar_posts
from core.modelos import Mencao


def test_coletar_posts_retorna_mencoes_em_sucesso(db):
    mock_page = MagicMock()
    mock_post = MagicMock()
    mock_post.query_selector.return_value.text_content.return_value = "candidato X ligado a Y"
    mock_post.query_selector.return_value.get_attribute.return_value = "/p/123"
    mock_page.query_selector_all.return_value = [mock_post]
    with patch("core.coletores.instagram._abrir_pagina", return_value=mock_page):
        mencoes = coletar_posts("@canal_politico", limite=5)
    assert isinstance(mencoes, list)
    assert len(mencoes) == 1
    assert isinstance(mencoes[0], Mencao)


def test_coletar_posts_retorna_vazio_em_block(db):
    with patch("core.coletores.instagram._abrir_pagina", side_effect=Exception("login required")):
        mencoes = coletar_posts("@canal", limite=5)
    assert mencoes == []
