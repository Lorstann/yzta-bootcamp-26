"""
backend/config.py
B10: Ortam değişkenlerini merkezi olarak okuyan config modülü.
Pydantic BaseSettings ile .env dosyasından otomatik okur.
"""

from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LlmProvider = Literal["openai", "anthropic", "bedrock", "gemini"]

_INSECURE_JWT_DEFAULTS = {
    "change-me-in-production",
    "change-me-in-production-use-a-long-random-string",
}


class Settings(BaseSettings):
    # Veritabanı — default is for local docker-compose only (port 5433).
    database_url: str = "postgresql+asyncpg://equa:equa_dev@localhost:5433/equa"

    # Güvenlik
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # LLM / AI (A1)
    llm_provider: LlmProvider = "gemini"
    llm_api_key: str = ""
    llm_model: str = "gemini-3.5-flash-lite"

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
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Rate limiting (requests per window)
    rate_limit_login_per_minute: int = 20
    rate_limit_stream_per_minute: int = 60

    # File storage (curriculum uploads)
    storage_backend: Literal["local", "s3"] = "local"
    s3_bucket: str = ""
    s3_region: str = "eu-central-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    local_storage_dir: str = "var/uploads"
    max_upload_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @model_validator(mode="after")
    def reject_insecure_production_secrets(self) -> "Settings":
        if self.app_env.lower() == "production":
            if self.jwt_secret in _INSECURE_JWT_DEFAULTS or len(self.jwt_secret) < 32:
                raise ValueError(
                    "JWT_SECRET must be set to a strong random value "
                    "(≥32 chars) when APP_ENV=production"
                )
            if "equa_dev" in self.database_url or "localhost" in self.database_url:
                raise ValueError(
                    "DATABASE_URL must not use local/dev defaults when APP_ENV=production"
                )
        return self


# Tekil instance — her yerden `from backend.config import settings` ile çağrılır.
settings = Settings()
