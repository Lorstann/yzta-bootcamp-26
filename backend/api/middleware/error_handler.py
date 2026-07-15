"""
backend/api/middleware/error_handler.py
B7: Global hata yakalayıcı middleware.

FastAPI'nin tüm yakalanmamış hatalarını envelope formatına çevirir.
Böylece frontend her zaman tutarlı bir JSON cevabı alır.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.domain.errors.app_error import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Tüm error handler'ları uygulamaya kaydeder. main.py'den çağrılır."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Uygulama iş mantığı hataları (AppError)."""
        logger.warning(
            "AppError: %s | path=%s | code=%s",
            exc.message, request.url.path, exc.code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": {"code": exc.code, "message": exc.message, "details": None},
                "meta": {},
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Pydantic doğrulama hataları (eksik/yanlış alan)."""
        errors = exc.errors()
        logger.warning(
            "ValidationError: %s hata | path=%s",
            len(errors), request.url.path,
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "İstek verisi geçersiz",
                    "details": errors,
                },
                "meta": {},
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """404, 403, 401 gibi HTTP hataları."""
        logger.warning(
            "HTTPException: %s | path=%s | detail=%s",
            exc.status_code, request.url.path, exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                    "details": None,
                },
                "meta": {},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Beklenmedik tüm hatalar — asla stack trace dışarıya sızmasın."""
        logger.error(
            "UnhandledException: %s | path=%s",
            type(exc).__name__, request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Beklenmedik bir hata oluştu",
                    "details": None,
                },
                "meta": {},
            },
        )
