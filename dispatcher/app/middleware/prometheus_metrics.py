"""
Prometheus Metrics Endpoint — Dispatcher.
prometheus_client kütüphanesi ile standart Prometheus formatında metrik sunar.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


# ============================================================
# Prometheus Metrikleri
# ============================================================

REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Toplam istek sayısı",
    ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "gateway_request_duration_seconds",
    "İstek yanıt süresi (saniye)",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ERROR_COUNT = Counter(
    "gateway_errors_total",
    "Toplam hata sayısı",
    ["method", "endpoint", "status_code"]
)

ACTIVE_REQUESTS = Gauge(
    "gateway_active_requests",
    "Aktif istek sayısı"
)

UPSTREAM_RESPONSE_TIME = Histogram(
    "gateway_upstream_response_seconds",
    "Upstream servis yanıt süresi",
    ["service"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Prometheus uyumlu metrik toplama middleware'i.
    Her HTTP isteği için counter, histogram ve gauge günceller.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # /metrics ve /health endpoint'lerini metrikten hariç tut
        if request.url.path in ("/metrics", "/health"):
            return await call_next(request)

        method = request.method
        path = self._normalize_path(request.url.path)

        ACTIVE_REQUESTS.inc()
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            ERROR_COUNT.labels(method=method, endpoint=path, status_code="500").inc()
            ACTIVE_REQUESTS.dec()
            raise e

        duration = time.time() - start_time

        # Metrikleri güncelle
        status = str(response.status_code)
        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)

        if response.status_code >= 400:
            ERROR_COUNT.labels(method=method, endpoint=path, status_code=status).inc()

        ACTIVE_REQUESTS.dec()
        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Path'i normalize eder. ID'leri {id} ile değiştirir.
        /api/products/abc123 → /api/products/{id}
        """
        parts = path.strip("/").split("/")
        normalized = []
        for i, part in enumerate(parts):
            if len(part) == 24 and all(c in "0123456789abcdef" for c in part):
                normalized.append("{id}")
            else:
                normalized.append(part)
        return "/" + "/".join(normalized)


def get_prometheus_metrics() -> Response:
    """Prometheus formatında metrikleri döner."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
