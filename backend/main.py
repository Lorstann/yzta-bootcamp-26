"""
backend/main.py
FastAPI uygulama giriş noktası.
"""

from fastapi import FastAPI

from backend.api.routes import health
from backend.api.middleware.error_handler import register_error_handlers
from backend.utils.logger import setup_logging

# Loglama sistemini başlat
setup_logging()

app = FastAPI(
    title="Equa API",
    version="1.0.0",
    description="Equa B2B2C MVP API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Global error handler'ları kaydet (B7)
register_error_handlers(app)

# Router'ları kaydet
app.include_router(health.router, prefix="/api/v1")