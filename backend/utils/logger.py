"""
backend/utils/logger.py
B7: Merkezi loglama yapılandırması.

Kullanım:
    from backend.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("İşlem tamamlandı", extra={"user_id": "123"})
"""

import logging
import sys
from backend.config import settings


def setup_logging() -> None:
    """Uygulama başlarken bir kez çağrılır. Tüm log formatını ayarlar."""

    log_level = getattr(logging, settings.log_level.upper(), logging.DEBUG)

    # Format: zaman | seviye | modül | mesaj
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Daha önce handler eklendiyse tekrar ekleme
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Gürültülü kütüphaneleri sustur
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.log_level == "debug" else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Modül adıyla logger döner. Her dosyada kullanılır."""
    return logging.getLogger(name)
