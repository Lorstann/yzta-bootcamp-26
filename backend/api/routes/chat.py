"""
backend/api/routes/chat.py
B5: POST /api/v1/chat/stream — SSE streaming chat endpoint.
"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.api.controllers.chat_controller import chat_stream
from backend.api.dependencies.auth import CurrentUser
from backend.domain.schemas.chat import ChatRequest
from backend.services.auth_service import decode_access_token
import uuid

router = APIRouter()
_bearer = HTTPBearer(auto_error=False)


def _optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser | None:
    if credentials is None or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return CurrentUser(
            id=uuid.UUID(payload["sub"]),
            tenant_id=uuid.UUID(payload["tenant_id"]),
            role=str(payload.get("role", "student")),
            email=str(payload.get("email", "")),
        )
    except Exception:
        return None


@router.post(
    "/chat/stream",
    tags=["chat"],
    summary="Öğrenci mesajına SSE stream yanıtı döner",
)
async def stream_chat_endpoint(
    request: ChatRequest,
    user: CurrentUser | None = Depends(_optional_user),
):
    return await chat_stream(request, user=user)
