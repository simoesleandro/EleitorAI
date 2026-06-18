from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    admin_pass: str = "eleitorai2026"
    secret_key: str = "dev-secret-change-me"
    db_path: str = "data/eleitorai.db"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
