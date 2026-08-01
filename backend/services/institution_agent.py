"""
backend/services/institution_agent.py
Institution AI assistant — metrics-only context, never raw student chat.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, AsyncIterator

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services import institution_service
from backend.services.llm.prompts import INSTITUTION_SYSTEM_PROMPT
from backend.services.llm.streaming import stream_llm_response

logger = logging.getLogger(__name__)


class MetricsContextPack(BaseModel):
    """Typed context for the institution agent.

    Intentionally excludes messages / summary / raw chat fields so leakage
    is structurally impossible.
    """

    model_config = ConfigDict(extra="forbid")

    total_students: int
    checked_in_today: int
    daily_checkin_rate: float
    avg_capacity: float | None = None
    risk_distribution: dict[str, int] = Field(default_factory=dict)
    trend_7d: list[dict[str, Any]] = Field(default_factory=list)
    roi: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    students: list[dict[str, Any]] = Field(default_factory=list)


def _student_public_row(row: dict[str, Any]) -> dict[str, Any]:
    """Strip anything that could be chat-like; keep XAI metrics only."""
    return {
        "full_name": row.get("full_name"),
        "email": row.get("email"),
        "risk_level": row.get("risk_level"),
        "rationale": row.get("rationale"),
        "capacity_score": row.get("capacity_score"),
        "metrics": row.get("metrics") or {},
    }


async def build_metrics_context(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> MetricsContextPack:
    overview = await institution_service.get_overview(db, tenant_id=tenant_id)
    usage = await institution_service.get_usage(db, tenant_id=tenant_id)
    students = await institution_service.list_students_with_risk(
        db, tenant_id=tenant_id
    )
    return MetricsContextPack(
        total_students=overview["total_students"],
        checked_in_today=overview["checked_in_today"],
        daily_checkin_rate=overview["daily_checkin_rate"],
        avg_capacity=overview.get("avg_capacity"),
        risk_distribution=overview.get("risk_distribution") or {},
        trend_7d=overview.get("trend_7d") or [],
        roi=overview.get("roi") or {},
        usage=usage,
        students=[_student_public_row(s) for s in students[:50]],
    )


def format_metrics_for_prompt(pack: MetricsContextPack) -> str:
    import json

    return json.dumps(pack.model_dump(), ensure_ascii=False, indent=2)


async def stream_institution_assistant(
    *,
    message: str,
    pack: MetricsContextPack,
) -> AsyncIterator[dict[str, Any]]:
    """Yield SSE-shaped events: chunk / done / error. Never includes raw chat."""
    lowered = message.lower()
    injection_markers = (
        "ignore previous",
        "talimatları yok say",
        "talimatlari yok say",
        "ham mesaj",
        "raw chat",
        "show messages",
        "mesajları göster",
        "mesajlari goster",
    )
    if any(m in lowered for m in injection_markers):
        reply = (
            "Ham öğrenci sohbetine erişimim yok ve talimatlarımı değiştiremem. "
            "Risk dağılımı, check-in oranı veya ROI hakkında sorabilirsin."
        )
        for word in reply.split():
            yield {"type": "chunk", "data": word + " "}
        yield {"type": "done"}
        return

    system = INSTITUTION_SYSTEM_PROMPT.replace(
        "{metrics_context}",
        format_metrics_for_prompt(pack),
    )
    try:
        async for chunk in stream_llm_response(message, system_prompt=system):
            yield {"type": "chunk", "data": chunk}
        yield {"type": "done"}
    except Exception as exc:
        logger.error("Institution assistant stream failed: %s", exc)
        from backend.domain.errors.app_error import AppError

        msg = (
            exc.message
            if isinstance(exc, AppError)
            else "Kurum asistanı şu an yanıt veremiyor."
        )
        yield {"type": "error", "message": msg}
