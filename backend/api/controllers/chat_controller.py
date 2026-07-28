"""
backend/api/controllers/chat_controller.py
B5/A7: Chat SSE + RAG context inject + check-in persist.
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
from backend.domain.schemas.chat import ChatRequest
from backend.repositories.checkin_repo import CheckinRepository
from backend.repositories.user_repo import StudentProfileRepository
from backend.services.chat_service import stream_chat_response
from backend.services.checkin_service import persist_turn_and_tasks
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


async def _event_generator(
    request: ChatRequest,
    *,
    user: CurrentUser | None,
):
    tenant_id = user.tenant_id if user else request.tenant_id
    user_id = user.id if user else None
    full_parts: list[str] = []
    curriculum_context = ""
    memory_context = ""

    async with AsyncSessionLocal() as db:
        try:
            await apply_tenant_context(db, tenant_id)
            curriculum_context = await retrieve_curriculum_context(
                db, tenant_id=tenant_id, query=request.message, top_k=4
            )
            if user_id:
                memory_context = await _build_memory_context(
                    db, tenant_id=tenant_id, user_id=user_id
                )
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("RAG retrieve failed: %s", exc)

    combined_context = "\n\n".join(
        p for p in (curriculum_context, memory_context) if p
    )

    capacity = None
    if user_id:
        async with AsyncSessionLocal() as db:
            try:
                await apply_tenant_context(db, tenant_id)
                profile = await StudentProfileRepository(db).get_by_user_id(user_id)
                capacity = profile.capacity_score if profile else None
                await db.commit()
            except Exception:
                await db.rollback()

    async for event in stream_chat_response(
        message=request.message,
        curriculum_context=combined_context or "",
    ):
        if event.get("type") == "chunk":
            full_parts.append(event.get("data", ""))
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        elif event.get("type") == "done":
            tasks = event.get("weekly_tasks")
            if tasks:
                event = {
                    **event,
                    "weekly_tasks": limit_tasks(tasks, capacity),
                }
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            assistant_text = "".join(full_parts)
            if user_id:
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
                        else:
                            await persist_turn_and_tasks(
                                db,
                                session_id=request.session_id,
                                tenant_id=tenant_id,
                                user_id=user_id,
                                user_message=request.message,
                                assistant_message=assistant_text,
                                weekly_tasks=event.get("weekly_tasks"),
                            )
                        await db.commit()
                    except Exception as exc:
                        await db.rollback()
                        logger.error("Chat persist failed: %s", exc)
        else:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def chat_stream(
    request: ChatRequest,
    user: CurrentUser | None = None,
) -> StreamingResponse:
    logger.info(
        "Chat stream başlatıldı | session_id=%s tenant_id=%s auth=%s",
        request.session_id,
        user.tenant_id if user else request.tenant_id,
        bool(user),
    )
    return StreamingResponse(
        _event_generator(request, user=user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
