from unittest.mock import patch
from veritas.seed_base import seed_base_fatos
from core.modelos import FactCheck


def test_seed_base_fatos_chama_scrapers_e_indexa(monkeypatch):
    fake_lupa = [FactCheck(titulo="A", veiculo="Lupa", url="u1", data="2026-01-01",
                            veredito_original="falso", claim_checada="x", explicacao="y")]
    fake_boatos = [FactCheck(titulo="B", veiculo="Boatos", url="u2", data="2026-01-01",
                              veredito_original="verdadeiro", claim_checada="w", explicacao="z")]
    with patch("veritas.seed_base.scraper_lupa", return_value=fake_lupa), \
         patch("veritas.seed_base.scraper_boatos", return_value=fake_boatos), \
         patch("veritas.seed_base.scraper_fato_fake", return_value=[]), \
         patch("veritas.seed_base.scraper_checamos", return_value=[]), \
         patch("veritas.seed_base.scraper_estadao_verifica", return_value=[]), \
         patch("veritas.seed_base.indexar") as mock_indexar:
        result = seed_base_fatos()
    assert result["total"] == 2
    assert result["por_veiculo"]["Lupa"] == 1
    assert result["por_veiculo"]["Boatos"] == 1
    assert mock_indexar.call_count == 2
