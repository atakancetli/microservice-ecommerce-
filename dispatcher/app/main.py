"""
Dispatcher (API Gateway) - Mikroservis Mimarisi
Tüm dış isteklerin tek giriş noktası.

Sorumluluklar:
- URL tabanlı yönlendirme (routing)
- Merkezi yetkilendirme (JWT auth)
- Trafik loglama
- Rate limiting
- Hata yönetimi (doğru HTTP status kodları)
"""
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.interfaces import (
    ServiceInfo, LogEntry, LogLevel, HttpMethod,
)
from app.routes.router import DispatcherRouter
from app.middleware.auth_middleware import AuthMiddlewareService
from app.services.proxy_service import ProxyServiceImpl
from app.services.log_service import RequestLogger
from app.services.rate_limiter import RateLimiterService


# ============================================================
# Servis instance'ları (Dependency Injection hazırlığı)
# ============================================================

router_service = DispatcherRouter()
auth_service = AuthMiddlewareService()
proxy_service = ProxyServiceImpl()
logger_service = RequestLogger()
rate_limiter = RateLimiterService(max_requests=100, window_seconds=60)


# ============================================================
# Uygulama yaşam döngüsü
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma: servisleri kaydet."""
    # Mikroservisleri kaydet
    await router_service.register_service(
        ServiceInfo(name="auth-service", base_url=settings.AUTH_SERVICE_URL)
    )
    await router_service.register_service(
        ServiceInfo(name="product-service", base_url=settings.PRODUCT_SERVICE_URL)
    )
    await router_service.register_service(
        ServiceInfo(name="order-service", base_url=settings.ORDER_SERVICE_URL)
    )

    print(f"🚀 Dispatcher starting on port {settings.PORT}")
    print(f"📡 Auth Service: {settings.AUTH_SERVICE_URL}")
    print(f"📡 Product Service: {settings.PRODUCT_SERVICE_URL}")
    print(f"📡 Order Service: {settings.ORDER_SERVICE_URL}")

    yield

    print("🛑 Dispatcher shutting down")


# ============================================================
# FastAPI uygulaması
# ============================================================

app = FastAPI(
    title="Dispatcher - API Gateway",
    description="Mikroservis mimarisinin tek giriş noktası. "
                "Tüm istekleri ilgili servislere yönlendirir.",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# Health & Metrics endpoint'leri (Public)
# ============================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Dispatcher sağlık kontrolü."""
    services = await router_service.get_registered_services()
    return {
        "status": "healthy",
        "service": "dispatcher",
        "registered_services": len(services),
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrikleri için istatistikler."""
    stats = await logger_service.get_stats()
    return stats


@app.get("/logs", tags=["Monitoring"])
async def get_logs(
    level: str = None,
    service: str = None,
    limit: int = 100,
):
    """Log kayıtlarını getir."""
    log_level = LogLevel[level.upper()] if level else None
    logs = await logger_service.get_logs(
        level=log_level, service=service, limit=limit
    )
    return {
        "count": len(logs),
        "logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "message": log.message,
                "service": log.service,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "response_time_ms": log.response_time_ms,
            }
            for log in logs
        ],
    }


# ============================================================
# API Gateway — Catch-all proxy route
# ============================================================

@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Gateway"],
)
async def gateway_proxy(request: Request, path: str):
    """
    Tüm /api/* isteklerini ilgili mikroservise yönlendirir.
    Akış: Route Resolution → Auth Check → Proxy → Log
    """
    import time
    start_time = time.time()
    full_path = f"/api/{path}"

    # ─── 1. Route Resolution ───
    route = await router_service.resolve_route(full_path)
    if route is None:
        await _log_request(full_path, request.method, 404, start_time)
        raise HTTPException(
            status_code=404,
            detail=f"Route not found: {full_path}",
        )

    # ─── 2. Auth Check (public route'lar hariç) ───
    if not await auth_service.is_public_route(full_path):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            await _log_request(full_path, request.method, 401, start_time)
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Provide Bearer token.",
            )

        token = auth_header.split(" ", 1)[1]
        user = await auth_service.authenticate(token)

        if user is None:
            await _log_request(full_path, request.method, 401, start_time)
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token.",
            )

        # Yetkilendirme kontrolü
        try:
            method_enum = HttpMethod[request.method]
        except KeyError:
            method_enum = HttpMethod.GET

        if not await auth_service.authorize(user, full_path, method_enum):
            await _log_request(full_path, request.method, 403, start_time)
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions.",
            )

    # ─── 3. Request Body Parse ───
    body = None
    if request.method in ("POST", "PUT", "PATCH"):
        try:
            body = await request.json()
        except Exception:
            body = None

    # ─── 4. Proxy Forward ───
    result = await proxy_service.forward_request(
        method=request.method,
        target_url=route.target_url,
        headers=dict(request.headers),
        body=body,
        query_params=dict(request.query_params),
    )

    status_code = result["status_code"]
    response_body = result["body"]

    # ─── 5. Log ───
    await _log_request(full_path, request.method, status_code, start_time)

    # ─── 6. Response ───
    if isinstance(response_body, dict):
        return JSONResponse(status_code=status_code, content=response_body)
    else:
        return JSONResponse(
            status_code=status_code,
            content={"data": response_body},
        )


# ============================================================
# Helper fonksiyonlar
# ============================================================

async def _log_request(
    path: str, method: str, status_code: int, start_time: float
):
    """İstek logunu kaydet."""
    import time
    response_time = (time.time() - start_time) * 1000
    level = LogLevel.ERROR if status_code >= 400 else LogLevel.INFO

    await logger_service.log(LogEntry(
        timestamp=datetime.now(),
        level=level,
        message=f"{method} {path} → {status_code}",
        service="dispatcher",
        method=method,
        path=path,
        status_code=status_code,
        response_time_ms=round(response_time, 2),
    ))
