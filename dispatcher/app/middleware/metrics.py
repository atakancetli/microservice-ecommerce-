"""
Prometheus Metrics Middleware — Dispatcher.
İstek sayısı, yanıt süresi ve hata oranı metriklerini toplar.
"""
import time
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.models.interfaces import LogEntry, LogLevel


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Her istek için metrik toplayan middleware.
    Prometheus uyumlu metrikler:
    - request_count: Toplam istek sayısı
    - request_duration_seconds: Yanıt süresi
    - error_count: Hata sayısı
    """

    def __init__(self, app, logger_service=None):
        super().__init__(app)
        self._logger = logger_service
        self._request_count = 0
        self._error_count = 0
        self._total_duration = 0.0

    async def dispatch(self, request: Request, call_next) -> Response:
        """Her isteği yakalar, zamanlama ve loglama yapar."""
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            self._error_count += 1
            raise e

        duration = time.time() - start_time
        self._request_count += 1
        self._total_duration += duration

        # Hata kontrolü
        if response.status_code >= 400:
            self._error_count += 1

        # Log kaydet
        if self._logger and request.url.path.startswith("/api"):
            level = LogLevel.ERROR if response.status_code >= 400 else LogLevel.INFO
            await self._logger.log(LogEntry(
                timestamp=datetime.now(),
                level=level,
                message=f"{request.method} {request.url.path} → {response.status_code}",
                service="dispatcher",
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                response_time_ms=round(duration * 1000, 2),
            ))

        return response

    def get_metrics(self) -> dict:
        """Prometheus formatında metrikleri döner."""
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "avg_duration_ms": (
                (self._total_duration / self._request_count * 1000)
                if self._request_count > 0
                else 0
            ),
        }
