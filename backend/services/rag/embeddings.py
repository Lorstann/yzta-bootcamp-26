"""
backend/services/rag/embeddings.py
A4: Embedding helpers (OpenAI or deterministic mock).
"""

from __future__ import annotations

import hashlib
import logging
import math

from backend.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 1536


def _mock_embedding(text: str) -> list[float]:
    """Deterministic pseudo-embedding for offline/dev without API key."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    seed = digest
    while len(values) < EMBEDDING_DIM:
        for b in seed:
            values.append((b / 255.0) * 2 - 1)
            if len(values) >= EMBEDDING_DIM:
                break
        seed = hashlib.sha256(seed).digest()
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    if not settings.llm_api_key:
        logger.info("LLM_API_KEY yok — mock embeddings kullanılıyor")
        return [_mock_embedding(t) for t in texts]

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.llm_api_key)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception as exc:
        logger.error("Embedding API hatası, mock'a düşülüyor: %s", exc)
        return [_mock_embedding(t) for t in texts]


async def embed_query(text: str) -> list[float]:
    vectors = await embed_texts([text])
    return vectors[0]
