from unittest.mock import patch, MagicMock
from core.llm import get_gemini_client, gerar_resposta, gerar_embedding
from core.config import get_settings


def test_get_gemini_client_returns_cached(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    c1 = get_gemini_client()
    c2 = get_gemini_client()
    assert c1 is c2


def test_gerar_resposta_returns_string(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "resposta teste"
    mock_client.models.generate_content.return_value = mock_response
    with patch("core.llm.get_gemini_client", return_value=mock_client):
        result = gerar_resposta("prompt teste")
        assert result == "resposta teste"


def test_gerar_embedding_returns_list_of_floats(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * 768)]
    mock_client.models.embed_content.return_value = mock_response
    with patch("core.llm.get_gemini_client", return_value=mock_client):
        emb = gerar_embedding("texto teste")
        assert isinstance(emb, list)
        assert len(emb) == 768
        assert all(isinstance(x, float) for x in emb)
