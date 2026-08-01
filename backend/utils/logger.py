"""
backend/utils/logger.py
B7: Merkezi loglama yapılandırması.

Kullanım:
    from backend.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("İşlem tamamlandı", extra={"user_id": "123"})
"""

import logging
import re
import sys

from backend.config import settings

_REDACT_KEYS = (
    "password",
    "password_hash",
    "passwordHash",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "jwt",
    "api_key",
    "llm_api_key",
)

# Only redact key=value / key: value pairs in already-formatted text.
_REDACT_RE = re.compile(
    r"(?i)\b(authorization|password(?:_hash)?|passwordHash|access_token|"
    r"refresh_token|token|jwt|llm_api_key|api_key)\b\s*[:=]\s*\S+"
)


class RedactingFormatter(logging.Formatter):
    """Format first, then redact — never mutate %-format placeholders."""

    def format(self, record: logging.LogRecord) -> str:
        for key in _REDACT_KEYS:
            if hasattr(record, key):
                setattr(record, key, "[REDACTED]")
        formatted = super().format(record)
        return _REDACT_RE.sub(r"\1=[REDACTED]", formatted)


def setup_logging() -> None:
    """Uygulama başlarken bir kez çağrılır. Tüm log formatını ayarlar."""

    log_level = getattr(logging, settings.log_level.upper(), logging.DEBUG)

    formatter = RedactingFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        for existing in root_logger.handlers:
            existing.setFormatter(formatter)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.log_level == "debug" else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Modül adıyla logger döner. Her dosyada kullanılır."""
    return logging.getLogger(name)
