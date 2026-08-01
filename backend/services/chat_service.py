"""
backend/services/chat_service.py
B5/B9: Chat servis katmanı.

Akış:
  1. Guardrail kontrolü (senkron)
  2. Guardrail tetiklendiyse → yönlendirme mesajını stream et
  3. Tetiklenmediyse → LLM'i stream et (history + stage-aware prompt)
  4. [DURUM] / [GOREVLER] bloklarını ayıkla; temiz metni kullanıcıya ver
  5. Yapısal sinyalleri parse et; görevleri çıkar
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, AsyncIterator, Mapping

from backend.services.checkin_flow import (
    MAX_TURNS,
    VALID_WORKLOAD,
    CheckinState,
    empty_state,
    merge_state,
    next_stage,
    should_force_complete,
)
from backend.services.llm.guardrails import check_for_risks
from backend.services.llm.prompts import build_checkin_prompt
from backend.services.llm.streaming import stream_llm_response

logger = logging.getLogger(__name__)

_TASK_BLOCK_RE = re.compile(
    r"\[GOREVLER\](.*?)\[/GOREVLER\]",
    re.DOTALL | re.IGNORECASE,
)
_STATE_BLOCK_RE = re.compile(
    r"\[DURUM\](.*?)\[/DURUM\]",
    re.DOTALL | re.IGNORECASE,
)

# Tags that must never reach the user bubble
_HIDDEN_OPEN = ("[DURUM]", "[GOREVLER]")
_HIDDEN_CLOSE = ("[/DURUM]", "[/GOREVLER]")
_MAX_TAG_LEN = max(len(t) for t in (*_HIDDEN_OPEN, *_HIDDEN_CLOSE))


class StreamSanitizer:
    """
    Strip [DURUM]...[/DURUM] and [GOREVLER]...[/GOREVLER] across chunk
    boundaries. Accumulates raw text for post-parse; yields clean text.
    """

    def __init__(self) -> None:
        self.raw_parts: list[str] = []
        self._buffer = ""
        self._hiding = False
        self._hide_until: str | None = None

    def feed(self, chunk: str) -> str:
        self.raw_parts.append(chunk)
        self._buffer += chunk
        out: list[str] = []

        while self._buffer:
            if self._hiding:
                close = self._hide_until or ""
                idx = self._buffer.upper().find(close.upper()) if close else -1
                if idx < 0:
                    # Keep a small tail in case close tag spans chunks
                    keep = min(len(close), len(self._buffer))
                    self._buffer = self._buffer[-keep:] if keep else ""
                    break
                # Drop through close tag
                self._buffer = self._buffer[idx + len(close) :]
                self._hiding = False
                self._hide_until = None
                continue

            # Look for next open tag
            open_idx = -1
            open_tag = ""
            close_tag = ""
            upper = self._buffer.upper()
            for ot, ct in zip(_HIDDEN_OPEN, _HIDDEN_CLOSE):
                i = upper.find(ot.upper())
                if i >= 0 and (open_idx < 0 or i < open_idx):
                    open_idx = i
                    open_tag = ot
                    close_tag = ct

            if open_idx < 0:
                # No open tag — emit all but keep a short tail for partial tags
                if len(self._buffer) > _MAX_TAG_LEN:
                    out.append(self._buffer[:-_MAX_TAG_LEN])
                    self._buffer = self._buffer[-_MAX_TAG_LEN:]
                break

            # Emit text before the tag
            if open_idx > 0:
                out.append(self._buffer[:open_idx])
            self._buffer = self._buffer[open_idx + len(open_tag) :]
            self._hiding = True
            self._hide_until = close_tag

        return "".join(out)

    def flush(self) -> str:
        """Emit remaining non-hidden buffer at end of stream."""
        if self._hiding:
            self._buffer = ""
            return ""
        leftover = self._buffer
        self._buffer = ""
        return leftover

    @property
    def raw(self) -> str:
        return "".join(self.raw_parts)


def _clamp_int(value: Any, lo: int, hi: int) -> int | None:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    if n < lo or n > hi:
        return None
    return n


def parse_state(text: str) -> CheckinState | None:
    """Extract and validate [DURUM]{...}[/DURUM] JSON block."""
    match = _STATE_BLOCK_RE.search(text)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("DURUM JSON parse failed | raw=%s", raw[:120])
        return None
    if not isinstance(data, dict):
        return None

    state: CheckinState = empty_state()
    energy = _clamp_int(data.get("enerji"), 1, 10)
    motivation = _clamp_int(data.get("motivasyon"), 1, 10)
    if energy is not None:
        state["enerji"] = energy
    if motivation is not None:
        state["motivasyon"] = motivation

    engel = data.get("engel")
    if isinstance(engel, str) and engel.strip():
        state["engel"] = engel.strip()[:500]

    yuk = data.get("yuk")
    if isinstance(yuk, str) and yuk.strip().lower() in VALID_WORKLOAD:
        state["yuk"] = yuk.strip().lower()

    if data.get("hazir") is True:
        state["hazir"] = True

    return state


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


_TECHNICAL_HINTS = (
    "solidity",
    "blockchain",
    "rust",
    "kotlin",
    "swift",
    "flutter",
    "unreal",
    "react",
    "node",
    "python",
    "java",
    "typescript",
    "javascript",
    "sql",
    "docker",
    "kubernetes",
    "aws",
    "api",
    "framework",
    "library",
    "npm",
    "git",
)


def _is_non_technical_task(task: str) -> bool:
    lowered = task.lower()
    return not any(h in lowered for h in _TECHNICAL_HINTS)


def _filter_tasks_for_curriculum(
    tasks: list[str], curriculum_context: str
) -> list[str]:
    """
    When curriculum is missing: keep only non-technical micro-steps.
    When present: drop tasks with no lexical overlap (S14), but always
    keep non-technical wellness tasks.
    """
    ctx = (curriculum_context or "").strip()
    no_curriculum = not ctx or ctx.startswith("Henüz müfredat")

    if no_curriculum:
        kept = [t for t in tasks if _is_non_technical_task(t)]
        return kept or tasks[:1]

    return _filter_tasks_to_curriculum(tasks, ctx)


_OFF_CURRICULUM_HINTS = (
    "solidity",
    "blockchain",
    "rust",
    "kotlin",
    "swift",
    "flutter",
    "unreal",
)


def is_likely_off_curriculum(message: str, curriculum_context: str) -> bool:
    """Heuristic: student asks for a known off-scope topic absent from RAG."""
    lowered = message.lower()
    ctx = (curriculum_context or "").lower()
    for hint in _OFF_CURRICULUM_HINTS:
        if hint in lowered and hint not in ctx:
            return True
    return False


def _filter_tasks_to_curriculum(tasks: list[str], curriculum_context: str) -> list[str]:
    """S14: Drop technical tasks with no lexical overlap vs retrieved curriculum."""
    ctx = curriculum_context.lower()
    kept: list[str] = []
    for task in tasks:
        if _is_non_technical_task(task):
            kept.append(task)
            continue
        tokens = [t for t in task.lower().replace(",", " ").split() if len(t) > 3]
        if not tokens or any(tok in ctx for tok in tokens):
            kept.append(task)
    return kept or tasks[:1]


async def stream_chat_response(
    message: str,
    curriculum_context: str = "",
    *,
    history: list[dict[str, Any]] | None = None,
    state: Mapping[str, Any] | None = None,
    turn_count: int = 0,
    stage: str | None = None,
    memory_context: str = "",
) -> AsyncIterator[dict]:
    """
    Öğrenci mesajına yanıt olarak SSE chunk'larını yield eder.

    Yields:
        {"type": "chunk", "data": "<temiz metin>"}
        {"type": "done", ... state, daily_tasks, checkin_completed}
        {"type": "error", "message": "..."}
    """
    # 1. Guardrail
    guardrail = check_for_risks(message)
    if guardrail.triggered:
        logger.warning("Guardrail tetiklendi | category=%s", guardrail.category)
        redirect_text = guardrail.template or ""
        for word in redirect_text.split():
            yield {"type": "chunk", "data": word + " "}
        yield {
            "type": "done",
            "guardrail_triggered": True,
            "guardrail_category": guardrail.category,
            "daily_tasks": None,
            "state": dict(state) if state else empty_state(),
            "checkin_completed": False,
            "stage": stage or "opening",
            "turn_count": turn_count,
        }
        return

    current_state: CheckinState = merge_state(
        empty_state(), dict(state) if state else None  # type: ignore[arg-type]
    )
    effective_turn = turn_count + 1
    effective_stage = stage or next_stage(current_state, turn_count)

    system_prompt = build_checkin_prompt(
        curriculum_context=curriculum_context or "",
        memory_context=memory_context or "",
        state=current_state,
        stage=effective_stage,  # type: ignore[arg-type]
        turn_count=effective_turn,
        max_turns=MAX_TURNS,
    )

    sanitizer = StreamSanitizer()

    try:
        async for chunk in stream_llm_response(
            message,
            system_prompt=system_prompt,
            history=history,
        ):
            clean = sanitizer.feed(chunk)
            if clean:
                yield {"type": "chunk", "data": clean}

        flush = sanitizer.flush()
        if flush:
            yield {"type": "chunk", "data": flush}

    except Exception as exc:
        logger.error("Chat streaming hatası: %s", exc)
        from backend.domain.errors.app_error import AppError

        err_msg = (
            exc.message
            if isinstance(exc, AppError)
            else "AI servisi şu an yanıt veremiyor."
        )
        yield {"type": "error", "message": err_msg}
        return

    raw = sanitizer.raw
    incoming = parse_state(raw)
    merged = merge_state(current_state, incoming)

    daily_tasks = _parse_tasks(raw)
    if daily_tasks:
        daily_tasks = _filter_tasks_for_curriculum(
            daily_tasks, curriculum_context or ""
        )
        if not daily_tasks:
            daily_tasks = None

    if daily_tasks or merged.get("hazir"):
        merged["hazir"] = True

    new_stage = next_stage(merged, effective_turn)
    completed = should_force_complete(effective_turn, daily_tasks)
    if completed:
        new_stage = "completed"

    logger.info(
        "Check-in turn done | turn=%s stage=%s→%s completed=%s tasks=%s energy=%s",
        effective_turn,
        effective_stage,
        new_stage,
        completed,
        len(daily_tasks) if daily_tasks else 0,
        merged.get("enerji"),
    )

    yield {
        "type": "done",
        "guardrail_triggered": False,
        "guardrail_category": None,
        "daily_tasks": daily_tasks,
        "state": merged,
        "checkin_completed": completed,
        "stage": new_stage,
        "turn_count": effective_turn,
    }
