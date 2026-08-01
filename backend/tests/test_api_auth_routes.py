"""
backend/tests/test_api_auth_routes.py
Auth + chat auth requirement + envelope shape (no DB required for most).
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import CurrentUser, get_current_user, require_roles
from backend.domain.errors.app_error import AppError
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_envelope(client: TestClient):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert body["error"] is None


def test_chat_stream_requires_auth(client: TestClient):
    res = client.post(
        "/api/v1/chat/stream",
        json={
            "session_id": str(uuid.uuid4()),
            "message": "Merhaba",
        },
    )
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHENTICATED"


def test_chat_rejects_tenant_id_in_body(client: TestClient):
    """extra=forbid — tenant_id must come from JWT only."""

    async def fake_user():
        return CurrentUser(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            role="student",
            email="s@equa.dev",
        )

    app.dependency_overrides[get_current_user] = fake_user
    try:
        res = client.post(
            "/api/v1/chat/stream",
            json={
                "tenant_id": str(uuid.uuid4()),
                "session_id": str(uuid.uuid4()),
                "message": "Merhaba",
            },
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
    finally:
        app.dependency_overrides.clear()


def test_institution_students_forbidden_for_student(client: TestClient):
    async def fake_student():
        return CurrentUser(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            role="student",
            email="s@equa.dev",
        )

    # require_roles("instructor","admin") wraps get_current_user
    student_dep = require_roles("instructor", "admin")
    app.dependency_overrides[get_current_user] = fake_student
    try:
        res = client.get(
            "/api/v1/institution/students",
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "FORBIDDEN"
    finally:
        app.dependency_overrides.clear()


def test_register_rejects_admin_role(client: TestClient):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "tenant_slug": "bootcamp-alpha",
            "email": "hacker@example.com",
            "password": "password123",
            "full_name": "Hacker",
            "role": "admin",
        },
    )
    assert res.status_code == 422
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
