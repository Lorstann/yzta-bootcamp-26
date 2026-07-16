"""
A3: Basit streaming yanıt fonksiyonu (LLM → token chunk).

Backend ekibi B5/B9'da POST /api/v1/chat/stream endpoint'ine bağlayacak.
API key yoksa geliştirme için mock streaming döner.
"""

import asyncio
from collections.abc import AsyncIterator

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from backend.domain.errors.app_error import AppError
from backend.services.llm.provider import get_llm_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MOCK_RESPONSE = (
    "Merhaba! Equa check-in asistanıyım. "
    "Bu hafta nasıl hissediyorsun? Kısa bir özet paylaşabilir misin?"
)


async def stream_llm_response(
    message: str,
    system_prompt: str | None = None,
) -> AsyncIterator[str]:
    """
    Kullanıcı mesajına karşılık LLM'den gelen token chunk'larını yield eder.

    Args:
        message: Öğrencinin chat mesajı.
        system_prompt: Opsiyonel sistem talimatı (check-in akışı için A6'da genişletilecek).

    Yields:
        Her iterasyonda bir metin parçası (token/chunk).
    """
    llm_settings = get_llm_settings()

    logger.info(
        "LLM streaming başlatılıyor | provider=%s model=%s has_api_key=%s",
        llm_settings.provider,
        llm_settings.model,
        bool(llm_settings.api_key),
    )

    if not llm_settings.api_key:
        logger.warning("LLM_API_KEY yok — mock streaming kullanılıyor")
        async for chunk in _mock_stream(message):
            yield chunk
        return

    try:
        messages: list[SystemMessage | HumanMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))

        if llm_settings.provider == "openai":
            llm = ChatOpenAI(
                api_key=llm_settings.api_key,
                model=llm_settings.model,
                streaming=True,
            )
        elif llm_settings.provider == "anthropic":
            llm = ChatAnthropic(
                api_key=llm_settings.api_key,
                model_name=llm_settings.model,
                streaming=True,
            )
        else:
            raise AppError(
                "Bedrock streaming henüz desteklenmiyor. LLM_PROVIDER=openai veya anthropic kullanın.",
                code="LLM_PROVIDER_UNSUPPORTED",
                status_code=501,
            )

        async for chunk in llm.astream(messages):
            text = _extract_chunk_text(chunk.content)
            if text:
                yield text

        logger.info("LLM streaming tamamlandı")

    except AppError:
        raise
    except Exception as err:
        logger.error(
            "LLM streaming başarısız | provider=%s err=%s",
            llm_settings.provider,
            err,
        )
        raise AppError(
            "AI servisi şu an yanıt veremiyor. Lütfen daha sonra tekrar deneyin.",
            code="LLM_UNAVAILABLE",
            status_code=503,
        ) from err


async def _mock_stream(message: str) -> AsyncIterator[str]:
    """API key olmadan local geliştirme için kelime kelime mock yanıt."""
    preview = message.strip()[:40] or "..."
    response = f"{MOCK_RESPONSE} (mock — mesajın: {preview})"
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
