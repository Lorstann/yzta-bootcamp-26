"""
backend/api/controllers/health_controller.py
B3: Health endpoint'in iş mantığı burada — route sadece yönlendirir.

Routes → Controllers → Services → Repositories katman ayrımı.
"""

from fastapi.responses import JSONResponse
from backend.utils.response import ok


def get_health() -> JSONResponse:
    """Servisin ayakta olduğunu doğrular ve envelope formatında döner."""
    return ok(data={"status": "healthy"})
