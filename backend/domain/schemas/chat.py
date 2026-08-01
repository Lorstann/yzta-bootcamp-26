# backend/domain/schemas/chat.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from uuid import UUID


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID = Field(..., description="Devam eden check-in oturumunun UUID'si")
    message: str = Field(
        ..., min_length=1, max_length=2000, description="Öğrencinin gönderdiği mesaj"
    )


class ChatStreamChunk(BaseModel):
    chunk: str = Field(..., description="LLM'den gelen anlık kelime parçası")


class ChatResponseData(BaseModel):
    session_id: UUID
    reply: str = Field(
        ..., description="AI'nin tamamlanmış yanıt metni (stream bitince birleştirilir)"
    )
    guardrail_triggered: bool = Field(
        default=False, description="S16 guardrail tetiklendi mi"
    )
    guardrail_category: Optional[str] = Field(
        default=None, description="Tetiklenen kategori: critical | dropout | depression"
    )
    daily_tasks: Optional[List[str]] = Field(
        default=None, description="Check-in sonunda önerilen max 3 günlük görev"
    )
