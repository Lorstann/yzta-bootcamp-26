"""
backend/services/curriculum_service.py
Institution curriculum upload / list / soft-delete.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.domain.errors.app_error import AppError
from backend.repositories.curriculum_repo import CurriculumRepository
from backend.services.document_text import ALLOWED_EXTENSIONS, extension_of, extract_text
from backend.services.rag.ingest import ingest_curriculum_text
from backend.services.storage import save_file

logger = logging.getLogger(__name__)


def serialize_curriculum(row) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "title": row.title,
        "description": row.description,
        "source_type": row.source_type,
        "file_name": getattr(row, "file_name", None),
        "chunk_count": getattr(row, "chunk_count", None),
        "is_active": bool(row.is_active),
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


async def list_curricula(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> list[dict[str, Any]]:
    repo = CurriculumRepository(db)
    rows = await repo.list_by_tenant(tenant_id)
    logger.info("Curriculum listed | tenant_id=%s count=%s", tenant_id, len(rows))
    return [serialize_curriculum(r) for r in rows]


async def upload_curriculum_file(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    uploaded_by: uuid.UUID,
    filename: str,
    data: bytes,
    title: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    ext = extension_of(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise AppError(
            f"Desteklenmeyen dosya türü: {ext or '(yok)'}. "
            f"İzin verilenler: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            code="VALIDATION_ERROR",
            status_code=422,
        )

    max_bytes = int(settings.max_upload_mb) * 1024 * 1024
    if len(data) > max_bytes:
        raise AppError(
            f"Dosya çok büyük (max {settings.max_upload_mb} MB)",
            code="VALIDATION_ERROR",
            status_code=422,
        )
    if not data:
        raise AppError(
            "Dosya boş",
            code="VALIDATION_ERROR",
            status_code=422,
        )

    text = extract_text(filename, data)
    if not text.strip():
        raise AppError(
            "Dosyadan metin çıkarılamadı",
            code="VALIDATION_ERROR",
            status_code=422,
        )

    try:
        uri = save_file(tenant_id, filename, data)
    except Exception as exc:
        logger.error("Curriculum file save failed: %s", exc)
        raise AppError(
            "Dosya kaydedilemedi",
            code="INTERNAL_ERROR",
            status_code=500,
        ) from exc

    resolved_title = (title or "").strip() or filename
    try:
        curriculum = await ingest_curriculum_text(
            db,
            tenant_id=tenant_id,
            title=resolved_title[:500],
            text=text,
            description=description,
            source_type="upload",
            file_name=filename,
            file_uri=uri,
            uploaded_by=uploaded_by,
        )
    except ValueError as exc:
        raise AppError(str(exc), code="VALIDATION_ERROR", status_code=422) from exc

    logger.info(
        "Curriculum uploaded | curriculum_id=%s tenant_id=%s file=%s",
        curriculum.id,
        tenant_id,
        filename,
    )
    return serialize_curriculum(curriculum)


async def create_curriculum_from_text(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    uploaded_by: uuid.UUID,
    title: str,
    text: str,
    description: str | None = None,
) -> dict[str, Any]:
    cleaned = (text or "").strip()
    if not cleaned:
        raise AppError(
            "Müfredat metni boş olamaz",
            code="VALIDATION_ERROR",
            status_code=422,
        )
    try:
        curriculum = await ingest_curriculum_text(
            db,
            tenant_id=tenant_id,
            title=title.strip()[:500],
            text=cleaned,
            description=description,
            source_type="paste",
            uploaded_by=uploaded_by,
        )
    except ValueError as exc:
        raise AppError(str(exc), code="VALIDATION_ERROR", status_code=422) from exc

    logger.info(
        "Curriculum pasted | curriculum_id=%s tenant_id=%s",
        curriculum.id,
        tenant_id,
    )
    return serialize_curriculum(curriculum)


async def soft_delete_curriculum(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    curriculum_id: uuid.UUID,
) -> dict[str, Any]:
    repo = CurriculumRepository(db)
    row = await repo.soft_delete(curriculum_id, tenant_id=tenant_id)
    if row is None:
        raise AppError("Müfredat bulunamadı", code="NOT_FOUND", status_code=404)
    logger.info(
        "Curriculum soft-deleted | curriculum_id=%s tenant_id=%s",
        curriculum_id,
        tenant_id,
    )
    return serialize_curriculum(row)
