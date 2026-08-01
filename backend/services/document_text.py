"""
backend/services/document_text.py
Extract plain text from uploaded curriculum / profile documents.
"""

from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = frozenset({".pdf", ".docx", ".txt", ".md"})


def extension_of(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def extract_text(filename: str, data: bytes) -> str:
    """Return extracted text or empty string on failure / unsupported type."""
    ext = extension_of(filename)
    if ext == ".pdf":
        return extract_text_from_pdf(data)
    if ext == ".docx":
        return _extract_docx(data)
    if ext in {".txt", ".md"}:
        return _extract_plain(data)
    logger.warning("Unsupported document type | ext=%s", ext)
    return ""


def extract_text_from_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    except Exception as exc:
        logger.error("PDF parse failed: %s", exc)
        return ""


def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document

        doc = Document(BytesIO(data))
        parts = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(parts).strip()
    except Exception as exc:
        logger.error("DOCX parse failed: %s", exc)
        return ""


def _extract_plain(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace").strip()
