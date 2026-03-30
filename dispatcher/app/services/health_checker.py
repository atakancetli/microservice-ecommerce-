"""
Health Check Endpoint'leri — Tüm Servisler.
Her servisin kendi sağlık durumunu raporlaması için ortak model.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Standart health check yanıt modeli."""
    status: str  # "healthy" / "degraded" / "unhealthy"
    service: str
    version: str = "1.0.0"
    uptime_seconds: Optional[float] = None
    checks: Optional[Dict[str, Any]] = None
    timestamp: str = datetime.utcnow().isoformat()


class ServiceHealthChecker:
    """
    Tüm downstream servislerin sağlık durumunu kontrol eder.
    Gateway üzerinden /health endpoint'ine istek atar.
    """

    def __init__(self):
        self._start_time = datetime.utcnow()

    def get_uptime(self) -> float:
        """Uptime'ı saniye olarak döner."""
        return (datetime.utcnow() - self._start_time).total_seconds()

    async def check_service(self, service_name: str, base_url: str) -> Dict[str, Any]:
        """Bir servisin sağlık durumunu kontrol eder."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/health", timeout=3.0)
                return {
                    "service": service_name,
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
        except Exception as e:
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": str(e),
            }

    async def check_all(self, services: Dict[str, str]) -> Dict[str, Any]:
        """Tüm servislerin sağlığını kontrol eder."""
        results = {}
        for name, url in services.items():
            results[name] = await self.check_service(name, url)

        all_healthy = all(r["status"] == "healthy" for r in results.values())
        return {
            "gateway": "healthy",
            "overall": "healthy" if all_healthy else "degraded",
            "services": results,
        }
