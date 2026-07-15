"""
backend/api/routes/health.py
B3: Health endpoint route tanımı — iş mantığı controller'da.
"""

from fastapi import APIRouter
from backend.api.controllers.health_controller import get_health

router = APIRouter()


@router.get("/health", tags=["system"])
def health_check():
    """Servisin sağlık durumunu döner."""
    return get_health()
