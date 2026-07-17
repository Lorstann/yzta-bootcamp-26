# backend/domain/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

class ChatRequest(BaseModel):
    tenant_id: UUID = Field(
        ..., 
        description="Kurumun benzersiz UUID'si. GEÇİCİ: S18 tamamlanınca token claim'inden alınmalı."
    )
    session_id: UUID = Field(..., description="Devam eden check-in oturumunun UUID'si")
    message: str = Field(..., min_length=1, max_length=2000, description="Öğrencinin gönderdiği mesaj")

class ChatStreamChunk(BaseModel):
    chunk: str = Field(..., description="LLM'den gelen anlık kelime parçası")

class ChatResponseData(BaseModel):
    session_id: UUID
    reply: str = Field(..., description="AI'nin tamamlanmış yanıt metni (stream bitince birleştirilir)")
    guardrail_triggered: bool = Field(default=False, description="S16 guardrail tetiklendi mi")
    guardrail_category: Optional[str] = Field(
        default=None, description="Tetiklenen kategori: critical | dropout | depression"
    )
    weekly_tasks: Optional[List[str]] = Field(
        default=None, description="Check-in sonunda önerilen max 3 görev"
    )