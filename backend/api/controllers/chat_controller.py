"""
backend/api/controllers/chat_controller.py
B5/A7: Chat SSE + RAG context inject + check-in/coach persist + history replay.
"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import CurrentUser
from backend.db.session import AsyncSessionLocal
from backend.db.tenant_context import apply_tenant_context
from backend.domain.errors.app_error import AppError
from backend.domain.schemas.chat import ChatRequest
from backend.repositories.checkin_repo import CheckinRepository
from backend.repositories.user_repo import StudentProfileRepository
from backend.services.chat_service import stream_chat_response, stream_coach_response
from backend.services.checkin_flow import (
    HISTORY_WINDOW,
    next_stage,
    resolve_mode,
    state_from_session,
)
from backend.services.checkin_service import persist_coach_turn, persist_turn_and_tasks
from backend.services.rag.retrieve import retrieve_curriculum_context
from backend.services.risk_service import record_high_risk_signal
from backend.services.task_balancing import limit_tasks

logger = logging.getLogger(__name__)


async def _build_memory_context(
    db: AsyncSession, *, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> str:
    """S13: past check-in summaries for prompt memory."""
    repo = CheckinRepository(db)
    summaries = await repo.list_recent_summaries(
        tenant_id=tenant_id, user_id=user_id, limit=3
    )
    if not summaries:
        return ""
    return "Geçmiş check-in özetleri:\n" + "\n".join(f"- {s}" for s in summaries)


async def _load_owned_session(
    db: AsyncSession,
    *,
    session_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
):
    repo = CheckinRepository(db)
    session = await repo.get_with_tasks(session_id)
    if session is None:
        raise AppError("Check-in session not found", code="NOT_FOUND", status_code=404)
    if session.tenant_id != tenant_id or session.user_id != user_id:
        raise AppError("Forbidden", code="FORBIDDEN", status_code=403)
    return session


def _history_window(messages: list | None) -> list[dict]:
    """Last N turns for LLM context (token control)."""
    rows = list(messages or [])
    if len(rows) > HISTORY_WINDOW:
        rows = rows[-HISTORY_WINDOW:]
    return [
        {"role": m.get("role"), "content": m.get("content", "")}
        for m in rows
        if isinstance(m, dict) and m.get("content")
    ]


def _task_titles(session) -> list[str]:
    tasks = getattr(session, "daily_tasks", None) or []
    return [t.title for t in tasks if getattr(t, "title", None)]


async def _event_generator(
    request: ChatRequest,
    *,
    user: CurrentUser,
):
    tenant_id = user.tenant_id
    user_id = user.id
    full_parts: list[str] = []
    curriculum_context = ""
    memory_context = ""
    history: list[dict] = []
    state: dict = {}
    turn_count = 0
    stage = "opening"
    session_status = "in_progress"
    today_tasks: list[str] = []
    mode = "checkin"

    async with AsyncSessionLocal() as db:
        try:
            await apply_tenant_context(db, tenant_id)
            session = await _load_owned_session(
                db,
                session_id=request.session_id,
                tenant_id=tenant_id,
                user_id=user_id,
            )
            history = _history_window(session.messages)
            state = dict(state_from_session(session))
            turn_count = int(getattr(session, "turn_count", None) or 0)
            session_status = getattr(session, "status", None) or "in_progress"
            today_tasks = _task_titles(session)
            # Always derive from signals so known Qs are never re-asked
            stage = next_stage(state, turn_count)
            mode = resolve_mode(session_status, stage)

            curriculum_context = await retrieve_curriculum_context(
                db, tenant_id=tenant_id, query=request.message, top_k=4
            )
            memory_context = await _build_memory_context(
                db, tenant_id=tenant_id, user_id=user_id
            )
            await db.commit()
        except AppError:
            await db.rollback()
            raise
        except Exception as exc:
            await db.rollback()
            logger.error("RAG retrieve failed: %s", exc)

    combined_context = curriculum_context or ""

    capacity = None
    async with AsyncSessionLocal() as db:
        try:
            await apply_tenant_context(db, tenant_id)
            profile = await StudentProfileRepository(db).get_by_user_id(user_id)
            capacity = profile.capacity_score if profile else None
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error(
                "Capacity lookup failed | user_id=%s err=%s", user_id, exc
            )

    stream = (
        stream_coach_response(
            message=request.message,
            curriculum_context=combined_context or "",
            history=history,
            memory_context=memory_context,
            today_state=state,
            today_tasks=today_tasks,
        )
        if mode == "coach"
        else stream_chat_response(
            message=request.message,
            curriculum_context=combined_context or "",
            history=history,
            state=state,
            turn_count=turn_count,
            stage=stage,
            memory_context=memory_context,
        )
    )

    async for event in stream:
        if event.get("type") == "chunk":
            full_parts.append(event.get("data", ""))
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        elif event.get("type") == "done":
            tasks = event.get("daily_tasks")
            if tasks and mode == "checkin":
                energy = (event.get("state") or {}).get("enerji")
                effective_capacity = capacity
                if energy is not None and int(energy) <= 4:
                    effective_capacity = min(
                        float(capacity) if capacity is not None else 40.0, 35.0
                    )
                event = {
                    **event,
                    "daily_tasks": limit_tasks(tasks, effective_capacity),
                }
            # Ensure frontend fields are always present
            event = {
                **event,
                "mode": event.get("mode") or mode,
                "checkin_completed": bool(event.get("checkin_completed")),
                "state": event.get("state") or state,
                "quick_replies": event.get("quick_replies"),
            }
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            assistant_text = "".join(full_parts)
            async with AsyncSessionLocal() as db:
                try:
                    await apply_tenant_context(db, tenant_id)
                    if event.get("guardrail_triggered"):
                        await record_high_risk_signal(
                            db,
                            tenant_id=tenant_id,
                            user_id=user_id,
                            category=event.get("guardrail_category") or "critical",
                        )
                    elif mode == "coach":
                        await persist_coach_turn(
                            db,
                            session_id=request.session_id,
                            tenant_id=tenant_id,
                            user_id=user_id,
                            user_message=request.message,
                            assistant_message=assistant_text,
                        )
                    else:
                        await persist_turn_and_tasks(
                            db,
                            session_id=request.session_id,
                            tenant_id=tenant_id,
                            user_id=user_id,
                            user_message=request.message,
                            assistant_message=assistant_text,
                            daily_tasks=event.get("daily_tasks"),
                            state=event.get("state"),
                            stage=event.get("stage"),
                            turn_count=event.get("turn_count"),
                            checkin_completed=bool(event.get("checkin_completed")),
                        )
                    await db.commit()
                except Exception as exc:
                    await db.rollback()
                    logger.error("Chat persist failed: %s", exc)
        else:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def chat_stream(
    request: ChatRequest,
    user: CurrentUser,
) -> StreamingResponse:
    # Validate session ownership before opening the SSE stream so clients
    # get a proper JSON error envelope (404/403) instead of a broken stream.
    async with AsyncSessionLocal() as db:
        try:
            await apply_tenant_context(db, user.tenant_id)
            await _load_owned_session(
                db,
                session_id=request.session_id,
                tenant_id=user.tenant_id,
                user_id=user.id,
            )
            await db.commit()
        except AppError:
            await db.rollback()
            raise
        except Exception as exc:
            await db.rollback()
            logger.error("Session ownership check failed: %s", exc)
            raise AppError(
                "Unable to verify chat session",
                code="INTERNAL_ERROR",
                status_code=500,
            ) from exc

    logger.info(
        "Chat stream başlatıldı | session_id=%s tenant_id=%s auth=%s",
        request.session_id,
        user.tenant_id,
        True,
    )
    return StreamingResponse(
        _event_generator(request, user=user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
