"""
backend/config.py
B10: Ortam değişkenlerini merkezi olarak okuyan config modülü.
Pydantic BaseSettings ile .env dosyasından otomatik okur.
"""

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LlmProvider = Literal["openai", "anthropic", "bedrock"]


class Settings(BaseSettings):
    # Veritabanı
    database_url: str = "postgresql+asyncpg://equa:equa_dev@localhost:5432/equa"

    # Güvenlik
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # LLM / AI (A1)
    llm_provider: LlmProvider = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    @field_validator("llm_provider", mode="before")
    @classmethod
    def normalize_llm_provider(cls, value: str) -> str:
        return value.lower().strip() if isinstance(value, str) else value

    # Tenant
    default_tenant_header: str = "X-Tenant-Id"

    # Loglama
    log_level: str = "debug"

    # Uygulama
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Tekil instance — her yerden `from backend.config import settings` ile çağrılır.
settings = Settings()
