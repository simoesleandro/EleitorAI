from unittest.mock import patch, MagicMock
from core.llm import (
    get_gemini_client,
    gerar_resposta,
    gerar_embedding,
    GeminiRateLimitError,
    GeminiServerError,
    _is_retryable_gemini_error,
)
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
    called_model = mock_client.models.embed_content.call_args.kwargs["model"]
    assert "embedding" in called_model.lower()
    assert "text-embedding-004" not in called_model, "text-embedding-004 is deprecated"


def test_is_retryable_gemini_error_429():
    assert _is_retryable_gemini_error(Exception("429 Resource exhausted"))
    assert _is_retryable_gemini_error(Exception("rate limit exceeded"))
    assert _is_retryable_gemini_error(Exception("quota exceeded"))


def test_is_retryable_gemini_error_5xx():
    assert _is_retryable_gemini_error(Exception("503 Service Unavailable"))
    assert _is_retryable_gemini_error(Exception("504 timeout"))


def test_is_retryable_gemini_error_4xx_nao_retryable():
    assert not _is_retryable_gemini_error(Exception("400 Bad Request"))
    assert not _is_retryable_gemini_error(Exception("401 Unauthorized"))
    assert not _is_retryable_gemini_error(Exception("invalid api key"))


def test_gerar_resposta_retried_em_429_e_sucesso(monkeypatch):
    """429 duas vezes, sucesso na terceira chamada."""
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    success = MagicMock()
    success.text = "ok apos retry"
    mock_client.models.generate_content.side_effect = [
        Exception("429 Resource exhausted"),
        Exception("429 rate limit"),
        success,
    ]
    with patch("core.llm.get_gemini_client", return_value=mock_client):
        result = gerar_resposta("prompt")
    assert result == "ok apos retry"
    assert mock_client.models.generate_content.call_count == 3


def test_gerar_resposta_exaure_tentativas_em_429(monkeypatch):
    """429 persistente -> levanta GeminiRateLimitError apos esgotar tentativas."""
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("429 quota exceeded")
    with patch("core.llm.get_gemini_client", return_value=mock_client):
        try:
            gerar_resposta("prompt")
        except GeminiRateLimitError:
            pass
        else:
            raise AssertionError("expected GeminiRateLimitError")
    assert mock_client.models.generate_content.call_count >= 2


def test_gerar_resposta_nao_retried_em_400(monkeypatch):
    """400 (client error) nao retry, propaga imediatamente."""
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("400 Bad Request: invalid prompt")
    with patch("core.llm.get_gemini_client", return_value=mock_client):
        try:
            gerar_resposta("prompt")
        except Exception as e:
            assert "400" in str(e)
        else:
            raise AssertionError("expected exception to propagate")
    assert mock_client.models.generate_content.call_count == 1


def test_gerar_embedding_retried_em_503(monkeypatch):
    """503 server error -> retry ate sucesso."""
    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    success = MagicMock()
    success.embeddings = [MagicMock(values=[0.5] * 768)]
    mock_client.models.embed_content.side_effect = [
        Exception("503 Service Unavailable"),
        success,
    ]
    with patch("core.llm.get_gemini_client", return_value=mock_client):
        emb = gerar_embedding("texto")
    assert len(emb) == 768
    assert emb[0] == 0.5
    assert mock_client.models.embed_content.call_count == 2


def test_gerar_resposta_inline_pydantic_refs_em_schema_aninhado(monkeypatch):
    """Pydantic nested models must be inlined (no $ref, no $defs) for Gemini."""
    from pydantic import BaseModel
    from typing import List

    class ClaimExtraida(BaseModel):
        texto: str
        confianca: float

    class VeritasReport(BaseModel):
        resumo: str
        claims: List[ClaimExtraida]

    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = VeritasReport(
        resumo="ok", claims=[ClaimExtraida(texto="x", confianca=0.9)]
    ).model_dump_json()
    mock_client.models.generate_content.return_value = mock_response

    with patch("core.llm.get_gemini_client", return_value=mock_client):
        gerar_resposta("prompt", response_schema=VeritasReport)

    config = mock_client.models.generate_content.call_args.kwargs["config"]
    raw = config.response_schema
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    if hasattr(raw, "to_dict"):
        raw = raw.to_dict()

    def _walk(node, path=""):
        if isinstance(node, dict):
            assert "$ref" not in node, f"$ref found at {path}: {node}"
            assert "$defs" not in node, f"$defs found at {path}: {node}"
            for k, v in node.items():
                _walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                _walk(v, f"{path}[{i}]")

    _walk(raw)
    assert isinstance(raw, dict)
    assert raw.get("type") == "object"
    assert "properties" in raw
    assert "claims" in raw["properties"]


# Campos que o Google AI (google-genai) rejeita em schemas JSON.
# Lista derivada de google.genai.models._Schema_to_mldev.
_GOOGLE_AI_FORBIDDEN_FIELDS = {
    "title",
    "default",
    "anyOf",
    "any_of",
    "minimum",
    "maximum",
    "min_items",
    "minItems",
    "max_items",
    "maxItems",
    "min_length",
    "minLength",
    "max_length",
    "maxLength",
    "min_properties",
    "minProperties",
    "max_properties",
    "maxProperties",
    "nullable",
    "pattern",
    "example",
    "property_ordering",
    "propertyOrdering",
}


def _walk_for_forbidden(node, path=""):
    """Recursively find any forbidden Google AI fields in a schema dict."""
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k in _GOOGLE_AI_FORBIDDEN_FIELDS:
                found.append(f"{path}.{k}")
            found.extend(_walk_for_forbidden(v, f"{path}.{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found.extend(_walk_for_forbidden(v, f"{path}[{i}]"))
    return found


def test_gerar_resposta_schema_strips_google_ai_forbidden_fields(monkeypatch):
    """Schema enviado ao Gemini nao pode conter title, default, anyOf, etc.

    O Google AI (google-genai <= 0.3.0) rejeita esses campos com ValueError
    em _Schema_to_mldev. Pydantic 2.x os adiciona por default em model_json_schema.
    """
    from typing import List, Optional
    from pydantic import BaseModel, Field

    class ClaimExtraida(BaseModel):
        texto: str
        sujeito: Optional[str] = None  # gera anyOf + default
        confianca: float = Field(ge=0.0, le=1.0)  # gera minimum + maximum
        checavel: bool = True  # gera default

    class VeritasReport(BaseModel):
        resumo: str
        claims: List[ClaimExtraida]

    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = VeritasReport(
        resumo="ok",
        claims=[ClaimExtraida(texto="x", confianca=0.9)],
    ).model_dump_json()
    mock_client.models.generate_content.return_value = mock_response

    with patch("core.llm.get_gemini_client", return_value=mock_client):
        gerar_resposta("prompt", response_schema=VeritasReport)

    config = mock_client.models.generate_content.call_args.kwargs["config"]
    raw = config.response_schema
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    if hasattr(raw, "to_dict"):
        raw = raw.to_dict()

    # Confirmar que os campos PROIBIDOS foram removidos
    forbidden_found = _walk_for_forbidden(raw)
    assert forbidden_found == [], (
        f"Schema enviado ao Gemini contem campos proibidos pelo Google AI: "
        f"{forbidden_found}. Schema: {raw}"
    )


def test_inline_pydantic_refs_strips_forbidden_fields_directly():
    """Testa a funcao _inline_pydantic_refs isoladamente com schema cheio
    de campos proibidos pelo Google AI."""
    import json
    from pydantic import BaseModel, Field
    from typing import List, Optional
    from core.llm import _inline_pydantic_refs

    class Claim(BaseModel):
        texto: str
        sujeito: Optional[str] = None
        confianca: float = Field(ge=0.0, le=1.0)
        checavel: bool = True

    class Report(BaseModel):
        claims: List[Claim]

    schema = Report.model_json_schema()
    inlined = _inline_pydantic_refs(schema)
    inlined_str = json.dumps(inlined)

    # $ref e $defs devem ser removidos (comportamento existente)
    assert "$ref" not in inlined_str
    assert "$defs" not in inlined_str

    # Campos proibidos pelo Google AI devem ser removidos (novo comportamento)
    forbidden_found = _walk_for_forbidden(inlined)
    assert forbidden_found == [], (
        f"Campos proibidos pelo Google AI ainda presentes no schema: "
        f"{forbidden_found}. Schema: {inlined_str[:500]}"
    )


def test_gerar_resposta_real_call_with_veritas_schema(monkeypatch):
    """Teste integracao: chama gerar_resposta com _ListaClaims (o schema que
    quebrou o job #9) e valida que o config passado ao Gemini nao vai levantar
    ValueError 'title parameter is not supported in Google AI'.

    Mockamos apenas a chamada HTTP, deixando o processamento de schema real.
    """
    from pydantic import BaseModel
    from typing import List
    from core.modelos import ClaimExtraida

    class _ListaClaims(BaseModel):
        claims: List[ClaimExtraida]

    get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"claims": [{"texto": "test", "confianca": 0.9}]}'
    mock_client.models.generate_content.return_value = mock_response

    with patch("core.llm.get_gemini_client", return_value=mock_client):
        result = gerar_resposta("prompt", response_schema=_ListaClaims)

    # Validar que a chamada foi feita sem erro (sem ValueError do Google AI)
    assert mock_client.models.generate_content.call_count == 1

    # Validar o schema enviado
    config = mock_client.models.generate_content.call_args.kwargs["config"]
    raw = config.response_schema
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    if hasattr(raw, "to_dict"):
        raw = raw.to_dict()

    forbidden_found = _walk_for_forbidden(raw)
    assert forbidden_found == [], (
        f"Schema _ListaClaims contem campos proibidos: {forbidden_found}"
    )

    # Validar que o resultado foi parseado corretamente
    assert isinstance(result, _ListaClaims)
    assert len(result.claims) == 1
    assert result.claims[0].texto == "test"


