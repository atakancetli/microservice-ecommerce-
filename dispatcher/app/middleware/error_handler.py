"""
Dispatcher — Gelişmiş hata yönetimi.
Tüm hataları merkezi olarak yakalar ve uygun HTTP yanıtları döner.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPException handler.
    Tüm HTTPException'ları standart formatta döner.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic validasyon hatası handler.
    Request body validasyon hatalarını 422 ile döner.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "detail": "Validation Error",
            "errors": errors,
            "path": str(request.url.path),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Beklenmeyen hata handler.
    Tüm yakalanmamış hataları 500 ile döner.
    Detay bilgisi production'da gizlenir.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal Server Error",
            "message": str(exc) if __debug__ else "An unexpected error occurred.",
            "path": str(request.url.path),
        },
    )


def register_error_handlers(app):
    """Tüm hata handler'larını FastAPI uygulamasına kaydeder."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
