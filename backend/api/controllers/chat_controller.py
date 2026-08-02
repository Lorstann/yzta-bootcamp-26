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
from backend.services.profile_service import merge_learned_profile, to_public_profile
from backend.services.rag.retrieve import retrieve_curriculum_context
from backend.services.risk_service import record_high_risk_signal
from backend.services.task_balancing import limit_tasks
from backend.services.wellbeing import build_wellbeing_context
from backend.services.capacity import estimate_live

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


def _interests_list(profile: dict | None, key: str) -> list[str]:
    if not profile:
        return []
    interests = profile.get("interests")
    if not isinstance(interests, dict):
        return []
    raw = interests.get(key) or []
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if isinstance(x, str) and x.strip()]


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
    profile_dict: dict | None = None
    wellbeing_context = ""

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
            if profile is not None:
                profile_dict = to_public_profile(profile)
                capacity = profile.capacity_score
            wellbeing_context = build_wellbeing_context(profile_dict, state)
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error(
                "Profile/wellbeing lookup failed | user_id=%s err=%s", user_id, exc
            )

    hobbies = _interests_list(profile_dict, "hobbies")
    city = (profile_dict or {}).get("city") if profile_dict else None
    track = (profile_dict or {}).get("program_track") if profile_dict else None

    stream = (
        stream_coach_response(
            message=request.message,
            curriculum_context=combined_context or "",
            history=history,
            memory_context=memory_context,
            wellbeing_context=wellbeing_context,
            today_state=state,
            today_tasks=today_tasks,
            program_track=track,
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
            wellbeing_context=wellbeing_context,
            program_track=track,
            hobbies=hobbies,
            city=city,
        )
    )

    async for event in stream:
        if event.get("type") == "chunk":
            full_parts.append(event.get("data", ""))
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        elif event.get("type") == "done":
            tasks = event.get("daily_tasks")
            if tasks and mode == "checkin":
                live = estimate_live(
                    float(capacity) if capacity is not None else None,
                    event.get("state") or state,
                )
                event = {
                    **event,
                    "daily_tasks": limit_tasks(tasks, live),
                }
            # Strip learned_profile from SSE (internal only)
            learned = event.pop("learned_profile", None)
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
                    elif event.get("off_topic"):
                        # Transcript only — do NOT advance check-in turn/signals
                        # and do NOT record a high-risk signal.
                        await persist_coach_turn(
                            db,
                            session_id=request.session_id,
                            tenant_id=tenant_id,
                            user_id=user_id,
                            user_message=request.message,
                            assistant_message=assistant_text,
                        )
                        logger.info(
                            "Off-topic turn persisted | session_id=%s family=%s mode=%s",
                            request.session_id,
                            event.get("scope_family"),
                            mode,
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
                    if learned:
                        await merge_learned_profile(
                            db, user_id=user_id, learned=learned
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
