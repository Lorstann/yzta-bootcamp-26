"""
backend/services/chat_service.py
B5/B9: Chat servis katmanı.

Akış:
  1. Guardrail kontrolü (senkron)
  2. Guardrail tetiklendiyse → yönlendirme mesajını stream et
  3. Tetiklenmediyse → LLM'i stream et (history + mode-aware prompt)
  4. [DURUM] / [GOREVLER] / [SECENEKLER] / [PROFIL] bloklarını ayıkla
  5. Yapısal sinyalleri parse et; görevleri / quick replies / learned profile çıkar
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, AsyncIterator, Mapping, Sequence

from backend.services.checkin_flow import (
    MAX_TURNS,
    VALID_WORKLOAD,
    CheckinState,
    coerce_scale,
    default_quick_replies,
    empty_state,
    merge_state,
    next_stage,
    should_force_complete,
)
from backend.services.llm.guardrails import check_for_risks
from backend.services.llm.prompts import build_checkin_prompt, build_coach_prompt
from backend.services.llm.scope_guard import (
    build_refusal_text,
    check_scope,
    refusal_quick_replies,
)
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
_CHOICE_BLOCK_RE = re.compile(
    r"\[SECENEKLER\](.*?)\[/SECENEKLER\]",
    re.DOTALL | re.IGNORECASE,
)
_PROFILE_BLOCK_RE = re.compile(
    r"\[PROFIL\](.*?)\[/PROFIL\]",
    re.DOTALL | re.IGNORECASE,
)

# Tags that must never reach the user bubble
_HIDDEN_OPEN = ("[DURUM]", "[GOREVLER]", "[SECENEKLER]", "[PROFIL]")
_HIDDEN_CLOSE = ("[/DURUM]", "[/GOREVLER]", "[/SECENEKLER]", "[/PROFIL]")
_MAX_TAG_LEN = max(len(t) for t in (*_HIDDEN_OPEN, *_HIDDEN_CLOSE))
_MAX_QUICK_REPLIES = 5
_MAX_QUICK_REPLY_LEN = 24

TaskItem = dict[str, str]  # {"title": ..., "description": ...}


class StreamSanitizer:
    """
    Strip [DURUM]/[GOREVLER]/[SECENEKLER]/[PROFIL] across chunk boundaries.
    Accumulates raw text for post-parse; yields clean text.
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
                    keep = min(len(close), len(self._buffer))
                    self._buffer = self._buffer[-keep:] if keep else ""
                    break
                self._buffer = self._buffer[idx + len(close) :]
                self._hiding = False
                self._hide_until = None
                continue

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
                if len(self._buffer) > _MAX_TAG_LEN:
                    out.append(self._buffer[:-_MAX_TAG_LEN])
                    self._buffer = self._buffer[-_MAX_TAG_LEN:]
                break

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
    energy = coerce_scale("enerji", data.get("enerji"))
    motivation = coerce_scale("motivasyon", data.get("motivasyon"))
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


def _split_task_line(line: str) -> TaskItem:
    """Parse 'title | description' or plain title into TaskItem."""
    cleaned = line.lstrip("- •*").strip()
    if "|" in cleaned:
        title, _, desc = cleaned.partition("|")
        return {
            "title": title.strip()[:200] or cleaned[:200],
            "description": desc.strip()[:500],
        }
    return {"title": cleaned[:200], "description": ""}


def _parse_tasks(text: str) -> list[TaskItem] | None:
    """[GOREVLER]...[/GOREVLER] bloğundan görev listesini çıkarır."""
    match = _TASK_BLOCK_RE.search(text)
    if not match:
        return None

    raw = match.group(1)
    tasks: list[TaskItem] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped.startswith(("-", "•", "*")):
            continue
        item = _split_task_line(stripped)
        if item["title"]:
            tasks.append(item)
    return tasks[:3] if tasks else None


def _parse_quick_replies(text: str) -> list[str] | None:
    """[SECENEKLER]...[/SECENEKLER] bloğundan chip listesini çıkarır."""
    match = _CHOICE_BLOCK_RE.search(text)
    if not match:
        return None

    raw = match.group(1)
    replies: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped.startswith(("-", "•", "*")):
            continue
        label = stripped.lstrip("- •*").strip()
        if not label:
            continue
        replies.append(label[:_MAX_QUICK_REPLY_LEN])
        if len(replies) >= _MAX_QUICK_REPLIES:
            break
    return replies or None


def _parse_learned_profile(text: str) -> dict[str, Any] | None:
    """Extract [PROFIL]{...}[/PROFIL] JSON if present."""
    match = _PROFILE_BLOCK_RE.search(text)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("PROFIL JSON parse failed | raw=%s", raw[:120])
        return None
    if not isinstance(data, dict):
        return None
    return data


_GENERIC_TASK_PATTERNS = (
    "gereksinimleri listele",
    "eksik kalan",
    "mentörüne",
    "mentore",
    "soru yaz",
    "planını gözden geçir",
    "planini gozden gecir",
    "bir konuyu tekrar",
    "konuyu gözden geçir",
    "konuyu gozden gecir",
    "tekrar et",
    "genel tekrar",
)


def _task_text(task: str | TaskItem) -> str:
    if isinstance(task, dict):
        return f"{task.get('title', '')} {task.get('description', '')}".strip()
    return str(task)


def _is_generic_task(task: str | TaskItem) -> bool:
    lowered = _task_text(task).lower()
    return any(p in lowered for p in _GENERIC_TASK_PATTERNS)


def drop_generic_tasks(tasks: list[TaskItem]) -> list[TaskItem]:
    """
    Soft backstop: drop generic tasks only if at least one specific remains.
    Never return an empty list when input was non-empty.
    """
    if not tasks:
        return tasks
    specific = [t for t in tasks if not _is_generic_task(t)]
    if specific:
        dropped = len(tasks) - len(specific)
        if dropped:
            logger.warning(
                "Dropped generic tasks | dropped=%s kept=%s",
                dropped,
                len(specific),
            )
        return specific
    logger.warning("All tasks generic — keeping as-is | count=%s", len(tasks))
    return tasks


_OFF_CURRICULUM_HINTS = (
    "solidity",
    "blockchain",
    "rust",
    "kotlin",
    "swift",
    "flutter",
    "unreal",
)

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


def _is_non_technical_task(task: str | TaskItem) -> bool:
    lowered = _task_text(task).lower()
    return not any(h in lowered for h in _TECHNICAL_HINTS)


def _is_wellness_task(
    task: str | TaskItem,
    *,
    hobbies: Sequence[str] | None = None,
    city: str | None = None,
) -> bool:
    """True if task references hobbies/city — exempt from curriculum overlap."""
    lowered = _task_text(task).lower()
    wellness_words = (
        "yürüyüş",
        "yuruyus",
        "park",
        "dinlen",
        "mola",
        "şarj",
        "sarj",
        "hobi",
        "kahve",
        "spor",
        "nefes",
        "uyku",
        "müzik",
        "muzik",
        "kitap",
        "doğa",
        "doga",
    )
    if any(w in lowered for w in wellness_words):
        return True
    for hobby in hobbies or []:
        if hobby and hobby.lower() in lowered:
            return True
    if city and city.lower() in lowered:
        return True
    return False


def _is_off_scope_task(task: str | TaskItem) -> bool:
    lowered = _task_text(task).lower()
    return any(h in lowered for h in _OFF_CURRICULUM_HINTS)


def _filter_tasks_for_curriculum(
    tasks: list[TaskItem],
    curriculum_context: str,
    *,
    track: str | None = None,
    hobbies: Sequence[str] | None = None,
    city: str | None = None,
) -> list[TaskItem]:
    """
    Drop truly off-scope tech (solidity etc.). When curriculum present,
    also require lexical overlap for technical tasks (wellness exempt).
    Never strip in-track technical tasks just because curriculum is empty.
    """
    ctx = (curriculum_context or "").strip()
    no_curriculum = not ctx or ctx.startswith("Henüz müfredat")
    track_l = (track or "").lower()

    kept: list[TaskItem] = []
    for task in tasks:
        if _is_wellness_task(task, hobbies=hobbies, city=city):
            kept.append(task)
            continue
        if _is_off_scope_task(task):
            # Keep if student's track explicitly mentions it
            if track_l and any(h in track_l for h in _OFF_CURRICULUM_HINTS):
                kept.append(task)
            continue
        if no_curriculum:
            kept.append(task)
            continue
        # Curriculum present: non-tech always kept; tech needs overlap
        if _is_non_technical_task(task):
            kept.append(task)
            continue
        text = _task_text(task).lower().replace(",", " ")
        tokens = [t for t in text.split() if len(t) > 3]
        ctx_l = ctx.lower()
        if not tokens or any(tok in ctx_l for tok in tokens):
            kept.append(task)
            continue
        # Track keyword overlap as fallback
        if track_l and any(tok in track_l for tok in tokens):
            kept.append(task)

    return kept or tasks[:1]


def _filter_tasks_to_curriculum(
    tasks: list[str] | list[TaskItem], curriculum_context: str
) -> list[str] | list[TaskItem]:
    """Legacy helper used by tests — wrap string tasks."""
    if tasks and isinstance(tasks[0], str):
        items: list[TaskItem] = [
            {"title": t, "description": ""} for t in tasks  # type: ignore[misc]
        ]
        filtered = _filter_tasks_for_curriculum(items, curriculum_context)
        return [t["title"] for t in filtered]
    return _filter_tasks_for_curriculum(tasks, curriculum_context)  # type: ignore[arg-type]


def is_likely_off_curriculum(message: str, curriculum_context: str) -> bool:
    """Heuristic: student asks for a known off-scope topic absent from RAG."""
    lowered = message.lower()
    ctx = (curriculum_context or "").lower()
    for hint in _OFF_CURRICULUM_HINTS:
        if hint in lowered and hint not in ctx:
            return True
    return False


async def stream_chat_response(
    message: str,
    curriculum_context: str = "",
    *,
    history: list[dict[str, Any]] | None = None,
    state: Mapping[str, Any] | None = None,
    turn_count: int = 0,
    stage: str | None = None,
    memory_context: str = "",
    wellbeing_context: str = "",
    program_track: str | None = None,
    hobbies: Sequence[str] | None = None,
    city: str | None = None,
) -> AsyncIterator[dict]:
    """
    Check-in mode: stage-aware streaming with signal/task extraction.

    Yields:
        {"type": "chunk", "data": "<temiz metin>"}
        {"type": "done", ... state, daily_tasks, checkin_completed, quick_replies,
         learned_profile}
        {"type": "error", "message": "..."}
    """
    guardrail = check_for_risks(message)
    if guardrail.triggered:
        logger.warning("Guardrail tetiklendi | category=%s", guardrail.category)
        redirect_text = guardrail.template or ""
        for word in redirect_text.split():
            yield {"type": "chunk", "data": word + " "}
        yield {
            "type": "done",
            "mode": "checkin",
            "guardrail_triggered": True,
            "guardrail_category": guardrail.category,
            "daily_tasks": None,
            "state": dict(state) if state else empty_state(),
            "checkin_completed": False,
            "stage": stage or "opening",
            "turn_count": turn_count,
            "quick_replies": None,
            "learned_profile": None,
            "off_topic": False,
            "scope_family": None,
        }
        return

    current_state: CheckinState = merge_state(
        empty_state(), dict(state) if state else None  # type: ignore[arg-type]
    )
    effective_stage = stage or next_stage(current_state, turn_count)

    scope = await check_scope(message)
    if not scope.in_scope:
        logger.info(
            "Off-topic (checkin) | family=%s reason=%s turn=%s",
            scope.family,
            scope.reason,
            turn_count,
        )
        refusal = build_refusal_text(
            family=scope.family,
            mode="checkin",
            stage=effective_stage,
            turn_count=turn_count,
            program_track=program_track,
            blocker=current_state.get("engel"),
        )
        for word in refusal.split():
            yield {"type": "chunk", "data": word + " "}
        yield {
            "type": "done",
            "mode": "checkin",
            "guardrail_triggered": False,
            "guardrail_category": None,
            "daily_tasks": None,
            "state": dict(current_state),
            "checkin_completed": False,
            "stage": effective_stage,
            "turn_count": turn_count,  # do NOT advance turn
            "quick_replies": refusal_quick_replies(
                mode="checkin", stage=effective_stage
            ),
            "learned_profile": None,
            "off_topic": True,
            "scope_family": scope.family,
        }
        return

    effective_turn = turn_count + 1

    system_prompt = build_checkin_prompt(
        curriculum_context=curriculum_context or "",
        memory_context=memory_context or "",
        wellbeing_context=wellbeing_context or "",
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
            daily_tasks,
            curriculum_context or "",
            track=program_track,
            hobbies=hobbies,
            city=city,
        )
        daily_tasks = drop_generic_tasks(daily_tasks)
        if not daily_tasks:
            daily_tasks = None

    if daily_tasks or merged.get("hazir"):
        merged["hazir"] = True

    new_stage = next_stage(merged, effective_turn)
    completed = should_force_complete(effective_turn, daily_tasks)  # type: ignore[arg-type]
    if completed:
        new_stage = "completed"

    quick_replies = _parse_quick_replies(raw)
    if not quick_replies and not completed:
        quick_replies = default_quick_replies(effective_stage) or None  # type: ignore[arg-type]
    if completed:
        quick_replies = None

    learned_profile = _parse_learned_profile(raw)

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
        "mode": "checkin",
        "guardrail_triggered": False,
        "guardrail_category": None,
        "daily_tasks": daily_tasks,
        "state": merged,
        "checkin_completed": completed,
        "stage": new_stage,
        "turn_count": effective_turn,
        "quick_replies": quick_replies,
        "learned_profile": learned_profile,
        "off_topic": False,
        "scope_family": None,
    }


async def stream_coach_response(
    message: str,
    curriculum_context: str = "",
    *,
    history: list[dict[str, Any]] | None = None,
    memory_context: str = "",
    wellbeing_context: str = "",
    today_state: Mapping[str, Any] | None = None,
    today_tasks: Sequence[str] | None = None,
    program_track: str | None = None,
) -> AsyncIterator[dict]:
    """
    Coach mode: real answers after check-in is complete.
    Does NOT parse [DURUM]/[GOREVLER] — coach must not assign tasks.
    Still parses [PROFIL] for silent learning.
    """
    guardrail = check_for_risks(message)
    if guardrail.triggered:
        logger.warning(
            "Guardrail tetiklendi (coach) | category=%s", guardrail.category
        )
        redirect_text = guardrail.template or ""
        for word in redirect_text.split():
            yield {"type": "chunk", "data": word + " "}
        yield {
            "type": "done",
            "mode": "coach",
            "guardrail_triggered": True,
            "guardrail_category": guardrail.category,
            "daily_tasks": None,
            "state": dict(today_state) if today_state else empty_state(),
            "checkin_completed": True,
            "stage": "completed",
            "turn_count": None,
            "quick_replies": None,
            "learned_profile": None,
            "off_topic": False,
            "scope_family": None,
        }
        return

    scope = await check_scope(message)
    if not scope.in_scope:
        logger.info(
            "Off-topic (coach) | family=%s reason=%s",
            scope.family,
            scope.reason,
        )
        blocker = None
        if today_state:
            raw = today_state.get("engel")
            blocker = raw if isinstance(raw, str) else None
        refusal = build_refusal_text(
            family=scope.family,
            mode="coach",
            stage="completed",
            turn_count=0,
            program_track=program_track,
            blocker=blocker,
        )
        for word in refusal.split():
            yield {"type": "chunk", "data": word + " "}
        yield {
            "type": "done",
            "mode": "coach",
            "guardrail_triggered": False,
            "guardrail_category": None,
            "daily_tasks": None,
            "state": dict(today_state) if today_state else empty_state(),
            "checkin_completed": True,
            "stage": "completed",
            "turn_count": None,
            "quick_replies": None,
            "learned_profile": None,
            "off_topic": True,
            "scope_family": scope.family,
        }
        return

    system_prompt = build_coach_prompt(
        curriculum_context=curriculum_context or "",
        memory_context=memory_context or "",
        wellbeing_context=wellbeing_context or "",
        today_state=today_state,
        today_tasks=today_tasks,
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
        logger.error("Coach streaming hatası: %s", exc)
        from backend.domain.errors.app_error import AppError

        err_msg = (
            exc.message
            if isinstance(exc, AppError)
            else "AI servisi şu an yanıt veremiyor."
        )
        yield {"type": "error", "message": err_msg}
        return

    learned_profile = _parse_learned_profile(sanitizer.raw)
    logger.info("Coach turn done | message_len=%s", len(message))

    yield {
        "type": "done",
        "mode": "coach",
        "guardrail_triggered": False,
        "guardrail_category": None,
        "daily_tasks": None,
        "state": dict(today_state) if today_state else empty_state(),
        "checkin_completed": True,
        "stage": "completed",
        "turn_count": None,
        "quick_replies": None,
        "learned_profile": learned_profile,
        "off_topic": False,
        "scope_family": None,
    }
