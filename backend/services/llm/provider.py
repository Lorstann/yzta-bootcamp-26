"""
A1: LLM sağlayıcı seçimi ve ortam değişkenlerinden okunan ayarlar.

Desteklenen sağlayıcılar: openai, anthropic, bedrock
API anahtarı ve model adı .env üzerinden gelir (config modülü).
"""

from dataclasses import dataclass
from typing import Literal

from backend.config import settings

LlmProvider = Literal["openai", "anthropic", "bedrock"]

DEFAULT_MODELS: dict[LlmProvider, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "bedrock": "anthropic.claude-3-haiku-20240307-v1:0",
}


@dataclass(frozen=True)
class LlmSettings:
    provider: LlmProvider
    api_key: str
    model: str


def get_llm_settings() -> LlmSettings:
    """Aktif LLM yapılandırmasını döner. A3 streaming bu modülü kullanacak."""
    provider = settings.llm_provider
    model = settings.llm_model or DEFAULT_MODELS[provider]
    return LlmSettings(
        provider=provider,
        api_key=settings.llm_api_key,
        model=model,
    )
