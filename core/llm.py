import logging
import threading
import time
from functools import lru_cache
from typing import Any, Callable, Optional, Type, Union

from google import genai
from google.genai import types
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from core.config import get_settings

logger = logging.getLogger(__name__)

# Gemini free tier: 15 RPM for Flash, 2 RPM for Pro.
# Conservative defaults for a single-key deployment.
MAX_CONCURRENT_LLM_CALLS = 4
MIN_INTERVAL_SECONDS = 4.0
RETRY_MAX_ATTEMPTS = 5
RETRY_MAX_WAIT_SECONDS = 60


class GeminiRateLimitError(Exception):
    """Gemini returned 429 / quota exceeded / rate limit hit."""


class GeminiServerError(Exception):
    """Gemini returned 5xx / unavailable."""


class _RateLimiter:
    """Thread-safe min-interval rate limiter (1 call per MIN_INTERVAL_SECONDS)."""

    def __init__(self, min_interval: float):
        self._lock = threading.Lock()
        self._last_call = 0.0
        self._min_interval = min_interval

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_call = time.monotonic()


_semaphore = threading.Semaphore(MAX_CONCURRENT_LLM_CALLS)
_rate_limiter = _RateLimiter(MIN_INTERVAL_SECONDS)


def _is_retryable_gemini_error(exc: BaseException) -> bool:
    """True for 429 / quota / 5xx / unavailable. False for client errors (4xx other)."""
    msg = str(exc).lower()
    retryable_tokens = ("429", "rate limit", "quota", "resource_exhausted",
                        "503", "504", "unavailable", "timeout", "deadline")
    return any(token in msg for token in retryable_tokens)


@retry(
    stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=1, max=RETRY_MAX_WAIT_SECONDS),
    retry=retry_if_exception_type((GeminiRateLimitError, GeminiServerError)),
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def _chamar_gemini(call_fn: Callable[[], Any], op_name: str) -> Any:
    """Wraps a Gemini call with rate limit + concurrency control + retry classification."""
    _rate_limiter.wait()
    with _semaphore:
        try:
            return call_fn()
        except Exception as e:
            if not _is_retryable_gemini_error(e):
                raise
            if any(t in str(e).lower() for t in ("429", "rate", "quota", "resource_exhausted")):
                raise GeminiRateLimitError(f"{op_name}: {e}") from e
            raise GeminiServerError(f"{op_name}: {e}") from e


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


@lru_cache
def get_model(name: str = "gemini-2.5-flash"):
    return get_gemini_client().models.get(name)


# Campos que o Google AI (google-genai <= 0.3.0) rejeita em schemas JSON.
# Lista derivada de google.genai.models._Schema_to_mldev.
# Pydantic 2.x adiciona esses campos por default em model_json_schema.
_GOOGLE_AI_FORBIDDEN_FIELDS = frozenset({
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
})


def _inline_pydantic_refs(schema: dict) -> dict:
    """Strip $defs, inline $ref, and remove Google AI-forbidden fields.

    Pydantic 2.x emits ``$ref`` / ``$defs`` for nested models, plus fields
    like ``title``, ``default``, ``anyOf``, ``minimum``, ``maximum`` that the
    Google AI structured output API rejects with ValueError.

    This walks the schema and:
    1. Replaces every ``{"$ref": "#/$defs/X"}`` with the inlined definition
    2. Removes the ``$defs`` block
    3. Removes any field in ``_GOOGLE_AI_FORBIDDEN_FIELDS``
    4. Flattens ``anyOf`` with a null option into ``type`` with ``nullable``
       is NOT done (Google AI rejects ``nullable`` too) - instead the first
       non-null type from anyOf is used, since Optional fields default to
       null anyway and Gemini can return null for absent fields.
    """
    defs = schema.pop("$defs", {}) if isinstance(schema, dict) else {}

    def _resolve(node):
        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                ref = node["$ref"]
                prefix = "#/$defs/"
                if ref.startswith(prefix) and ref[len(prefix):] in defs:
                    inlined = defs[ref[len(prefix):]]
                    return _resolve(inlined)
            result = {}
            for k, v in node.items():
                if k in _GOOGLE_AI_FORBIDDEN_FIELDS:
                    continue
                if k == "$defs":
                    continue
                if k == "anyOf" and isinstance(v, list):
                    # anyOf [{type: string}, {type: null}] -> pick first non-null
                    non_null = [
                        opt for opt in v
                        if not (isinstance(opt, dict) and opt.get("type") == "null")
                    ]
                    if non_null:
                        resolved = _resolve(non_null[0])
                        if isinstance(resolved, dict):
                            result.update(resolved)
                        continue
                result[k] = _resolve(v)
            return result
        if isinstance(node, list):
            return [_resolve(x) for x in node]
        return node

    return _resolve(schema)


def gerar_resposta(
    prompt: str,
    modelo: str = "gemini-2.5-flash",
    response_schema: Optional[Type[BaseModel]] = None,
) -> Union[str, BaseModel]:
    client = get_gemini_client()
    config_kwargs = {}
    if response_schema is not None:
        config_kwargs["response_mime_type"] = "application/json"
        if isinstance(response_schema, type) and issubclass(response_schema, BaseModel):
            schema_dict = response_schema.model_json_schema()
            config_kwargs["response_schema"] = _inline_pydantic_refs(schema_dict)
        else:
            config_kwargs["response_schema"] = response_schema
    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    def _call():
        return client.models.generate_content(model=modelo, contents=prompt, config=config)

    response = _chamar_gemini(_call, op_name=f"gerar_resposta:{modelo}")
    if response_schema is not None:
        return response_schema.model_validate_json(response.text)
    return response.text


EMBEDDING_MODEL = "gemini-embedding-001"


def gerar_embedding(texto: str) -> list[float]:
    client = get_gemini_client()

    def _call():
        return client.models.embed_content(model=EMBEDDING_MODEL, contents=texto)

    response = _chamar_gemini(_call, op_name=f"gerar_embedding:{EMBEDDING_MODEL}")
    return list(response.embeddings[0].values)
