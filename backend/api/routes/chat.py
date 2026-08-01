"""
backend/api/routes/chat.py
B5: POST /api/v1/chat/stream — SSE streaming chat endpoint (auth required).
"""

from fastapi import APIRouter, Depends

from backend.api.controllers.chat_controller import chat_stream
from backend.api.dependencies.auth import CurrentUser, require_roles
from backend.domain.schemas.chat import ChatRequest

router = APIRouter()

_student = require_roles("student")


@router.post(
    "/chat/stream",
    tags=["chat"],
    summary="Öğrenci mesajına SSE stream yanıtı döner",
)
async def stream_chat_endpoint(
    request: ChatRequest,
    user: CurrentUser = Depends(_student),
):
    return await chat_stream(request, user=user)
