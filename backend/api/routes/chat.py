"""
backend/api/routes/chat.py
B5: POST /api/v1/chat/stream — SSE streaming chat endpoint.
"""

from fastapi import APIRouter
from backend.domain.schemas.chat import ChatRequest
from backend.api.controllers.chat_controller import chat_stream

router = APIRouter()


@router.post(
    "/chat/stream",
    tags=["chat"],
    summary="Öğrenci mesajına SSE stream yanıtı döner",
    description=(
        "Öğrenci mesajını alır, guardrail kontrolü yapar, ardından "
        "LLM yanıtını Server-Sent Events (SSE) formatında akıtır. "
        "Her event JSON formatındadır: `{type, data}` veya `{type, guardrail_triggered, weekly_tasks}`."
    ),
)
async def stream_chat_endpoint(request: ChatRequest):
    return await chat_stream(request)
