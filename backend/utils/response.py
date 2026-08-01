"""
backend/utils/response.py
B3: Tüm API cevapları için standart envelope yardımcısı.

Kullanım:
    from backend.utils.response import ok, err

    return ok(data={"status": "healthy"})
    return err(message="Not found", code="NOT_FOUND", status_code=404)
"""

from typing import Any
from fastapi.responses import JSONResponse


def ok(data: Any = None, meta: dict = None, *, status_code: int = 200) -> JSONResponse:
    """Başarılı cevap envelope'u döner."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data if data is not None else {},
            "error": None,
            "meta": meta if meta is not None else {},
        },
    )


def err(
    message: str,
    code: str = "INTERNAL_ERROR",
    status_code: int = 500,
    details: Any = None,
) -> JSONResponse:
    """Hata cevabı envelope'u döner."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "meta": {},
        },
    )
