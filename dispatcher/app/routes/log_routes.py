"""
Log Table Endpoint — Dispatcher.
Loglama kayıtlarını tablo formatında sunan REST endpoint.
Filtreleme, sıralama ve pagination desteği.
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from app.services.log_service import RequestLogger

router = APIRouter(prefix="/logs", tags=["Monitoring"])


@router.get("/table", summary="Log Tablosu")
async def get_log_table(
    level: Optional[str] = Query(None, description="Log seviyesi filtresi"),
    service: Optional[str] = Query(None, description="Servis filtresi"),
    method: Optional[str] = Query(None, description="HTTP metot filtresi"),
    limit: int = Query(50, ge=1, le=500, description="Döndürülecek log sayısı"),
    offset: int = Query(0, ge=0, description="Atlanacak log sayısı"),
):
    """
    Log kayıtlarını tablo formatında döner.
    Filtreleme ve pagination desteği ile.
    """
    logger = RequestLogger()
    all_logs = await logger.get_logs(limit=limit + offset)
    
    # Filtreleme
    filtered = all_logs
    if level:
        filtered = [l for l in filtered if l.level.value == level.upper()]
    if service:
        filtered = [l for l in filtered if l.service == service]
    if method:
        filtered = [l for l in filtered if l.method == method.upper()]
    
    # Pagination
    paginated = filtered[offset:offset + limit]
    
    return {
        "total": len(filtered),
        "offset": offset,
        "limit": limit,
        "logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "response_time_ms": log.response_time_ms,
                "service": log.service,
                "message": log.message,
            }
            for log in paginated
        ],
    }


@router.get("/stats", summary="Log İstatistikleri")
async def get_log_stats():
    """Gateway log istatistiklerini döner."""
    logger = RequestLogger()
    stats = await logger.get_stats()
    return {
        "total_requests": stats.get("total_requests", 0),
        "error_count": stats.get("error_count", 0),
        "avg_response_time_ms": stats.get("avg_response_time_ms", 0),
        "timestamp": datetime.now().isoformat(),
    }
