"""
backend/domain/errors/app_error.py
B3: Uygulama geneli özel hata sınıfı.

Kullanım:
    raise AppError("Kayıt bulunamadı", code="NOT_FOUND", status_code=404)
"""


class AppError(Exception):
    """Tüm iş mantığı hatalarının temel sınıfı."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
