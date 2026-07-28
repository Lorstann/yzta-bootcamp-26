"""
backend/services/chat_service.py
B5/B9: Chat servis katmanı.

Akış:
  1. Guardrail kontrolü (senkron)
  2. Guardrail tetiklendiyse → yönlendirme mesajını stream et
  3. Tetiklenmediyse → LLM'i stream et
  4. Yanıt tamamlanınca [GOREVLER] bloğunu ayrıştır
"""

import logging
import re
from typing import AsyncIterator

from backend.services.llm.guardrails import check_for_risks
from backend.services.llm.streaming import stream_llm_response
from backend.services.llm.prompts import CHECKIN_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# [GOREVLER] bloğunu yakalamak için regex
_TASK_BLOCK_RE = re.compile(
    r"\[GOREVLER\](.*?)\[/GOREVLER\]",
    re.DOTALL | re.IGNORECASE,
)


async def stream_chat_response(
    message: str,
    curriculum_context: str = "",
) -> AsyncIterator[dict]:
    """
    Öğrenci mesajına yanıt olarak SSE chunk'larını yield eder.

    Yields:
        {"type": "chunk",    "data": "<metin parçası>"}
        {"type": "done",     "guardrail_triggered": bool, "guardrail_category": str|None, "weekly_tasks": list[str]|None}
        {"type": "error",    "message": "<hata mesajı>"}
    """

    # 1. Guardrail kontrolü
    guardrail = check_for_risks(message)
    if guardrail.triggered:
        logger.warning("Guardrail tetiklendi | category=%s", guardrail.category)
        # Yönlendirme mesajını kelime kelime stream et
        redirect_text = guardrail.template or ""
        for word in redirect_text.split():
            yield {"type": "chunk", "data": word + " "}
        yield {
            "type": "done",
            "guardrail_triggered": True,
            "guardrail_category": guardrail.category,
            "weekly_tasks": None,
        }
        return

    # 2. LLM streaming
    system_prompt = CHECKIN_SYSTEM_PROMPT.replace(
        "{curriculum_context}",
        curriculum_context or "Henüz müfredat yüklenmedi.",
    )

    full_response_parts: list[str] = []

    try:
        async for chunk in stream_llm_response(message, system_prompt=system_prompt):
            full_response_parts.append(chunk)
            yield {"type": "chunk", "data": chunk}

    except Exception as exc:
        logger.error("Chat streaming hatası: %s", exc)
        yield {"type": "error", "message": "AI servisi şu an yanıt veremiyor."}
        return

    # 3. [GOREVLER] bloğunu ayrıştır + S14 curriculum-only soft filter
    full_response = "".join(full_response_parts)
    weekly_tasks = _parse_tasks(full_response)
    if weekly_tasks and curriculum_context:
        weekly_tasks = _filter_tasks_to_curriculum(weekly_tasks, curriculum_context)

    yield {
        "type": "done",
        "guardrail_triggered": False,
        "guardrail_category": None,
        "weekly_tasks": weekly_tasks,
    }


def _filter_tasks_to_curriculum(tasks: list[str], curriculum_context: str) -> list[str]:
    """S14: Drop tasks with no lexical overlap vs retrieved curriculum."""
    ctx = curriculum_context.lower()
    kept: list[str] = []
    for task in tasks:
        tokens = [t for t in task.lower().replace(",", " ").split() if len(t) > 3]
        if not tokens or any(tok in ctx for tok in tokens):
            kept.append(task)
    return kept or tasks[:1]


def _parse_tasks(text: str) -> list[str] | None:
    """[GOREVLER]...[/GOREVLER] bloğundan görev listesini çıkarır."""
    match = _TASK_BLOCK_RE.search(text)
    if not match:
        return None

    raw = match.group(1)
    tasks = [
        line.lstrip("- •*").strip()
        for line in raw.splitlines()
        if line.strip().startswith(("-", "•", "*"))
    ]
    return tasks[:3] if tasks else None
