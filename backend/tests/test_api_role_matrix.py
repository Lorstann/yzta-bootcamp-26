"""Role × endpoint matrix (auth gates without DB)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import CurrentUser, get_current_user
from backend.main import app


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


STUDENT_GETS = [
    "/api/v1/tasks",
    "/api/v1/checkins/current",
    "/api/v1/checkins/history",
    "/api/v1/profiles/me",
    "/api/v1/profiles/me/stats",
]

STAFF_GETS = [
    "/api/v1/institution/students",
    "/api/v1/institution/roi",
    "/api/v1/institution/overview",
    "/api/v1/institution/usage",
    "/api/v1/institution/me",
]


@pytest.mark.parametrize("path", STUDENT_GETS)
def test_student_routes_forbid_instructor(client: TestClient, path: str):
    app.dependency_overrides[get_current_user] = _override("instructor")
    try:
        res = client.get(path, headers={"Authorization": "Bearer fake"})
        assert res.status_code == 403, path
        assert res.json()["error"]["code"] == "FORBIDDEN"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("path", STAFF_GETS)
def test_staff_routes_forbid_student(client: TestClient, path: str):
    app.dependency_overrides[get_current_user] = _override("student")
    try:
        res = client.get(path, headers={"Authorization": "Bearer fake"})
        assert res.status_code == 403, path
        assert res.json()["error"]["code"] == "FORBIDDEN"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("path", STUDENT_GETS + STAFF_GETS)
def test_all_protected_routes_require_auth(client: TestClient, path: str):
    res = client.get(path)
    assert res.status_code == 401, path
    assert res.json()["error"]["code"] == "UNAUTHENTICATED"


def test_settings_forbidden_for_instructor(client: TestClient):
    app.dependency_overrides[get_current_user] = _override("instructor")
    try:
        res = client.patch(
            "/api/v1/institution/settings",
            json={"revenue_per_student": 6000},
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_assistant_stream_forbidden_for_student(client: TestClient):
    app.dependency_overrides[get_current_user] = _override("student")
    try:
        res = client.post(
            "/api/v1/institution/assistant/stream",
            json={"message": "Risk nasıl?"},
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_chat_stream_forbidden_for_admin(client: TestClient):
    app.dependency_overrides[get_current_user] = _override("admin")
    try:
        res = client.post(
            "/api/v1/chat/stream",
            json={"session_id": str(uuid.uuid4()), "message": "hi"},
            headers={"Authorization": "Bearer fake"},
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()
