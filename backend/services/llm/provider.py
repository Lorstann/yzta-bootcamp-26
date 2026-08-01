"""
A1: LLM sağlayıcı seçimi ve ortam değişkenlerinden okunan ayarlar.

Desteklenen sağlayıcılar: gemini, openai, anthropic, bedrock
API anahtarı ve model adı .env üzerinden gelir (config modülü).
"""

from dataclasses import dataclass
from typing import Any, Literal

from backend.config import settings

LlmProvider = Literal["openai", "anthropic", "bedrock", "gemini"]

DEFAULT_MODELS: dict[LlmProvider, str] = {
    "gemini": "gemini-3.5-flash-lite",
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


def build_chat_llm(*, streaming: bool = True) -> Any:
    """
    LangChain chat model instance üretir.

    Gemini: ChatGoogleGenerativeAI
    OpenAI / Anthropic: mevcut LangChain sarmalayıcıları
    """
    llm_settings = get_llm_settings()

    if llm_settings.provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=llm_settings.model,
            google_api_key=llm_settings.api_key,
            streaming=streaming,
        )

    if llm_settings.provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=llm_settings.api_key,
            model=llm_settings.model,
            streaming=streaming,
        )

    if llm_settings.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            api_key=llm_settings.api_key,
            model_name=llm_settings.model,
            streaming=streaming,
        )

    from backend.domain.errors.app_error import AppError

    raise AppError(
        "Bedrock henüz desteklenmiyor. LLM_PROVIDER=gemini, openai veya anthropic kullanın.",
        code="LLM_PROVIDER_UNSUPPORTED",
        status_code=501,
    )
