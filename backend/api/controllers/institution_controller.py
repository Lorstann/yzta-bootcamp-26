"""
backend/api/controllers/institution_controller.py
"""

from __future__ import annotations

import json
import logging
import uuid

from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import CurrentUser
from backend.domain.errors.app_error import AppError
from backend.domain.schemas.institution import (
    InstitutionAssistantRequest,
    TenantSettingsUpdate,
)
from backend.services import institution_agent, institution_service
from backend.utils.response import ok

logger = logging.getLogger(__name__)


async def list_students(db: AsyncSession, user: CurrentUser):
    rows = await institution_service.list_students_with_risk(
        db, tenant_id=user.tenant_id
    )
    return ok(data={"students": rows})


async def get_student(db: AsyncSession, user: CurrentUser, student_id: uuid.UUID):
    data = await institution_service.get_student_detail(
        db, tenant_id=user.tenant_id, user_id=student_id
    )
    return ok(data=data)


async def get_roi(db: AsyncSession, user: CurrentUser):
    data = await institution_service.get_roi_metrics(db, tenant_id=user.tenant_id)
    return ok(data=data)


async def get_overview(db: AsyncSession, user: CurrentUser):
    data = await institution_service.get_overview(db, tenant_id=user.tenant_id)
    return ok(data=data)


async def get_usage(db: AsyncSession, user: CurrentUser):
    data = await institution_service.get_usage(db, tenant_id=user.tenant_id)
    return ok(data=data)


async def get_me(db: AsyncSession, user: CurrentUser):
    data = await institution_service.get_staff_me(
        db, tenant_id=user.tenant_id, user_id=user.id
    )
    return ok(data=data)


async def patch_settings(
    db: AsyncSession, user: CurrentUser, body: TenantSettingsUpdate
):
    if user.role != "admin":
        raise AppError("Forbidden", code="FORBIDDEN", status_code=403)
    data = await institution_service.update_tenant_settings(
        db,
        tenant_id=user.tenant_id,
        revenue_per_student=body.revenue_per_student,
    )
    return ok(data=data)


async def assistant_stream(
    db: AsyncSession, user: CurrentUser, body: InstitutionAssistantRequest
):
    pack = await institution_agent.build_metrics_context(
        db, tenant_id=user.tenant_id
    )
    # Structural guarantee: never include raw chat
    dumped = pack.model_dump()
    if "messages" in dumped or "raw_chat" in dumped:
        raise AppError(
            "Context pack integrity failure",
            code="INTERNAL_ERROR",
            status_code=500,
        )

    logger.info(
        "Institution assistant stream | tenant_id=%s user_id=%s",
        user.tenant_id,
        user.id,
    )

    async def _gen():
        async for event in institution_agent.stream_institution_assistant(
            message=body.message,
            pack=pack,
        ):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
