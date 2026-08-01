"""
A3: Basit streaming yanıt fonksiyonu (LLM → token chunk).

Backend ekibi B5/B9'da POST /api/v1/chat/stream endpoint'ine bağlayacak.
API key yoksa geliştirme için mock streaming döner.
"""

import asyncio
from collections.abc import AsyncIterator

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from backend.config import settings
from backend.domain.errors.app_error import AppError
from backend.services.llm.provider import build_chat_llm, get_llm_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MOCK_RESPONSE = (
    "Merhaba! Equa check-in asistanıyım. "
    "Bugün nasıl hissediyorsun? Kısa bir özet paylaşabilir misin?"
)


def build_llm_messages(
    message: str,
    system_prompt: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> list[BaseMessage]:
    """
    Build LangChain message list: optional system + prior turns + current human.
    history items: {"role": "user"|"assistant", "content": str}
    """
    messages: list[BaseMessage] = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    for turn in history or []:
        role = (turn.get("role") or "").lower()
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=message))
    return messages


async def stream_llm_response(
    message: str,
    system_prompt: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> AsyncIterator[str]:
    """
    Kullanıcı mesajına karşılık LLM'den gelen token chunk'larını yield eder.

    Args:
        message: Öğrencinin chat mesajı.
        system_prompt: Opsiyonel sistem talimatı.
        history: Önceki turlar (user/assistant). Varsayılan None — institution agent etkilenmez.

    Yields:
        Her iterasyonda bir metin parçası (token/chunk).
    """
    llm_settings = get_llm_settings()

    logger.info(
        "LLM streaming başlatılıyor | provider=%s model=%s has_key=%s history_turns=%s",
        llm_settings.provider,
        llm_settings.model,
        bool(llm_settings.api_key),
        len(history or []),
    )

    if not llm_settings.api_key:
        logger.warning("LLM_API_KEY yok — mock streaming kullanılıyor")
        async for chunk in _mock_stream(message):
            yield chunk
        return

    try:
        messages = build_llm_messages(message, system_prompt, history)

        llm = build_chat_llm(streaming=True)

        async for chunk in llm.astream(messages):
            text = _extract_chunk_text(chunk.content)
            if text:
                yield text

        logger.info("LLM streaming tamamlandı")

    except AppError:
        raise
    except Exception as err:
        err_text = str(err)
        is_quota = _is_quota_error(err_text)
        is_model_gone = _is_model_unavailable(err_text)
        logger.error(
            "LLM streaming başarısız | provider=%s quota=%s model_gone=%s err=%s",
            llm_settings.provider,
            is_quota,
            is_model_gone,
            err,
        )

        # Development: keep demo usable when Gemini quota/model fails.
        if (is_quota or is_model_gone) and settings.app_env.lower() == "development":
            logger.warning(
                "LLM kullanılamıyor — development mock streaming'e düşülüyor"
            )
            async for chunk in _mock_stream(
                message,
                quota_fallback=is_quota,
                model_fallback=is_model_gone,
            ):
                yield chunk
            return

        if is_quota:
            raise AppError(
                "AI kotası doldu. Birkaç dakika sonra tekrar dene "
                "veya .env içinde LLM_MODEL değerini değiştir "
                "(ör. gemini-3.5-flash-lite).",
                code="LLM_QUOTA_EXCEEDED",
                status_code=429,
            ) from err

        if is_model_gone:
            raise AppError(
                "Seçili AI modeli bu API anahtarı için kullanılamıyor. "
                ".env içinde LLM_MODEL=gemini-3.5-flash-lite dene.",
                code="LLM_MODEL_UNAVAILABLE",
                status_code=503,
            ) from err

        raise AppError(
            "AI servisi şu an yanıt veremiyor. Lütfen daha sonra tekrar deneyin.",
            code="LLM_UNAVAILABLE",
            status_code=503,
        ) from err


def _is_quota_error(err_text: str) -> bool:
    lowered = err_text.lower()
    return any(
        marker in lowered
        for marker in (
            "429",
            "resource_exhausted",
            "quota",
            "rate limit",
            "rate_limit",
        )
    )


def _is_model_unavailable(err_text: str) -> bool:
    lowered = err_text.lower()
    return any(
        marker in lowered
        for marker in (
            "404",
            "not_found",
            "no longer available",
            "is not found",
            "not supported",
        )
    )


async def _mock_stream(
    message: str,
    *,
    quota_fallback: bool = False,
    model_fallback: bool = False,
) -> AsyncIterator[str]:
    """API key olmadan local geliştirme için kelime kelime mock yanıt."""
    preview = message.strip()[:40] or "..."
    if quota_fallback:
        prefix = "Kota geçici olarak doldu; demo modundayım. "
    elif model_fallback:
        prefix = "Seçili model şu an API'de yok; demo modundayım. "
    else:
        prefix = ""
    response = (
        f"{prefix}Anladım, bugün biraz yorgun hissediyorsun gibi. "
        f"En zorlayan konu neydi kısaca? "
        f"[DURUM]{{\"enerji\":5,\"motivasyon\":4,\"engel\":null,\"yuk\":\"orta\",\"hazir\":false}}[/DURUM] "
        f"[GOREVLER]\n"
        f"- Bugün 20 dk müfredat tekrarı yap\n"
        f"- Kısa bir not al ve yarın kontrol et\n"
        f"[/GOREVLER] "
        f"(mock — mesajın: {preview})"
    )
    for word in response.split():
        yield word + " "
        await asyncio.sleep(0.03)


def _extract_chunk_text(content: str | list) -> str:
    """LangChain chunk içeriğini düz metne çevirir."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return ""
