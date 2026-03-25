"""
DispatcherRouter — URL tabanlı servis yönlendirme.
IRouter arayüzünün somut implementasyonu.
SOLID: Single Responsibility — yalnızca rota çözümleme.
"""
from typing import Dict, List, Optional

from app.models.interfaces import IRouter, ServiceInfo, RouteResult


class DispatcherRouter(IRouter):
    """
    Gelen istekleri URL yapısına göre ilgili mikroservise yönlendirir.
    Servis kaydı (service registry) pattern'i kullanır.
    """

    # URL prefix → servis adı eşleştirmesi
    ROUTE_MAP = {
        "/api/auth": "auth-service",
        "/api/products": "product-service",
        "/api/orders": "order-service",
    }

    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}

    async def register_service(self, service: ServiceInfo) -> None:
        """Bir mikroservisi servis kaydına ekler."""
        self._services[service.name] = service

    async def unregister_service(self, service_name: str) -> None:
        """
        Bir mikroservisi servis kaydından çıkarır.
        Raises ValueError: Servis bulunamazsa.
        """
        if service_name not in self._services:
            raise ValueError(f"Service not found: {service_name}")
        del self._services[service_name]

    async def resolve_route(self, path: str) -> Optional[RouteResult]:
        """
        URL path'ini analiz ederek hedef servisi belirler.
        /api/products/123/reviews → product-service
        /api/orders → order-service
        /api/unknown → None
        """
        for prefix, service_name in self.ROUTE_MAP.items():
            if path.startswith(prefix):
                if service_name in self._services:
                    service = self._services[service_name]
                    # Prefix'ten sonraki path kısmını al
                    remaining_path = path[len(prefix):]
                    target_url = f"{service.base_url}{remaining_path}"
                    return RouteResult(
                        target_url=target_url,
                        service_name=service_name,
                        path=path,
                    )
                # Servis kayıtlı değilse de None dön
                return None
        return None

    async def get_registered_services(self) -> List[ServiceInfo]:
        """Kayıtlı tüm servislerin listesini döner."""
        return list(self._services.values())
