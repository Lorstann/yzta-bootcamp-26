"""Curriculum upload service + role gates."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import CurrentUser, get_current_user
from backend.domain.errors.app_error import AppError
from backend.main import app
from backend.services import curriculum_service


@pytest.fixture
def client():
    return TestClient(app)


def _override(role: str):
    async def fake():
        return CurrentUser(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            role=role,
            email=f"{role}@equa.dev",
        )

    return fake


def test_curriculum_list_forbidden_for_student(client: TestClient):
    app.dependency_overrides[get_current_user] = _override("student")
    try:
        res = client.get(
            "/api/v1/institution/curriculum",
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_curriculum_upload_forbidden_for_instructor(client: TestClient):
    app.dependency_overrides[get_current_user] = _override("instructor")
    try:
        res = client.post(
            "/api/v1/institution/curriculum",
            files={"file": ("syllabus.txt", b"React week 1", "text/plain")},
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_curriculum_text_forbidden_for_student(client: TestClient):
    app.dependency_overrides[get_current_user] = _override("student")
    try:
        res = client.post(
            "/api/v1/institution/curriculum/text",
            json={"title": "Syl", "text": "React hooks"},
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_rejects_bad_extension():
    with pytest.raises(AppError) as exc:
        await curriculum_service.upload_curriculum_file(
            MagicMock(),
            tenant_id=uuid.uuid4(),
            uploaded_by=uuid.uuid4(),
            filename="malware.exe",
            data=b"x",
        )
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_from_text_happy_path():
    fake_row = MagicMock()
    fake_row.id = uuid.uuid4()
    fake_row.title = "React Bootcamp"
    fake_row.description = None
    fake_row.source_type = "paste"
    fake_row.file_name = None
    fake_row.chunk_count = 2
    fake_row.is_active = True
    fake_row.created_at = None

    with patch(
        "backend.services.curriculum_service.ingest_curriculum_text",
        new=AsyncMock(return_value=fake_row),
    ) as ingest:
        result = await curriculum_service.create_curriculum_from_text(
            MagicMock(),
            tenant_id=uuid.uuid4(),
            uploaded_by=uuid.uuid4(),
            title="React Bootcamp",
            text="Week 1: hooks\nWeek 2: routing",
        )
    assert result["title"] == "React Bootcamp"
    assert result["source_type"] == "paste"
    ingest.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_from_text_rejects_empty():
    with pytest.raises(AppError) as exc:
        await curriculum_service.create_curriculum_from_text(
            MagicMock(),
            tenant_id=uuid.uuid4(),
            uploaded_by=uuid.uuid4(),
            title="Empty",
            text="   ",
        )
    assert exc.value.status_code == 422
