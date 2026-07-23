"""
backend/api/controllers/chat_controller.py
B5: Chat endpoint controller — SSE StreamingResponse üretir.
"""

import json
import logging
from fastapi.responses import StreamingResponse

from backend.services.chat_service import stream_chat_response
from backend.domain.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)


async def _event_generator(request: ChatRequest):
    """SSE formatında chunk'ları yield eder."""
    async for event in stream_chat_response(
        message=request.message,
        curriculum_context="",  # A7 (RAG) hazır olduğunda buraya gelecek
    ):
        # SSE formatı: "data: <json>\n\n"
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    POST /api/v1/chat/stream controller'ı.
    SSE text/event-stream yanıtı döner.
    """
    logger.info(
        "Chat stream başlatıldı | session_id=%s tenant_id=%s",
        request.session_id,
        request.tenant_id,
    )
    return StreamingResponse(
        _event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Nginx proxy için
        },
    )
