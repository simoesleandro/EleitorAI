from functools import lru_cache
from typing import Optional, Type, Union

from google import genai
from google.genai import types
from pydantic import BaseModel

from core.config import get_settings


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


@lru_cache
def get_model(name: str = "gemini-2.5-flash"):
    return get_gemini_client().models.get(name)


def gerar_resposta(
    prompt: str,
    modelo: str = "gemini-2.5-flash",
    response_schema: Optional[Type[BaseModel]] = None,
) -> Union[str, BaseModel]:
    client = get_gemini_client()
    config_kwargs = {}
    if response_schema is not None:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = response_schema
    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
    response = client.models.generate_content(
        model=modelo,
        contents=prompt,
        config=config,
    )
    if response_schema is not None:
        return response_schema.model_validate_json(response.text)
    return response.text


def gerar_embedding(texto: str) -> list[float]:
    client = get_gemini_client()
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=texto,
    )
    return list(response.embeddings[0].values)
