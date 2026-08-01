"""
backend/main.py
FastAPI uygulama giriş noktası.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import health, chat, auth, checkins, profiles, institution
from backend.api.middleware.error_handler import register_error_handlers
from backend.api.middleware.rate_limit import RateLimitMiddleware
from backend.config import settings
from backend.utils.logger import setup_logging

setup_logging()

app = FastAPI(
    title="Equa API",
    version="1.0.0",
    description="Equa B2B2C MVP API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

register_error_handlers(app)

app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(checkins.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(institution.router, prefix="/api/v1")
