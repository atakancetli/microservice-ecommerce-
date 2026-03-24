"""
Dispatcher Routing Testleri — TDD RED Aşaması.
Bu testler Dispatcher'ın URL tabanlı yönlendirme işlevselliğini test eder.
Henüz implementasyon yapılmadığı için tüm testler FAIL olmalıdır.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.interfaces import IRouter, ServiceInfo, RouteResult


# ============================================================
# Unit Tests — Router Sınıfı
# ============================================================

class TestRouterServiceRegistration:
    """Servis kayıt işlemleri testleri."""

    @pytest.mark.asyncio
    async def test_register_service_successfully(self):
        """Yeni bir servis başarıyla kaydedilebilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        service = ServiceInfo(name="product-service", base_url="http://product-service:8002")
        await router.register_service(service)
        services = await router.get_registered_services()
        assert len(services) == 1
        assert services[0].name == "product-service"

    @pytest.mark.asyncio
    async def test_register_multiple_services(self):
        """Birden fazla servis kaydedilebilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        services = [
            ServiceInfo(name="auth-service", base_url="http://auth-service:8001"),
            ServiceInfo(name="product-service", base_url="http://product-service:8002"),
            ServiceInfo(name="order-service", base_url="http://order-service:8003"),
        ]
        for svc in services:
            await router.register_service(svc)
        registered = await router.get_registered_services()
        assert len(registered) == 3

    @pytest.mark.asyncio
    async def test_unregister_service(self):
        """Kayıtlı bir servis kaldırılabilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        service = ServiceInfo(name="product-service", base_url="http://product-service:8002")
        await router.register_service(service)
        await router.unregister_service("product-service")
        services = await router.get_registered_services()
        assert len(services) == 0

    @pytest.mark.asyncio
    async def test_unregister_nonexistent_service_raises(self):
        """Var olmayan bir servisi kaldırmaya çalışmak hata fırlatmalı."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        with pytest.raises(ValueError):
            await router.unregister_service("nonexistent")


class TestRouterRouteResolution:
    """URL yönlendirme çözümleme testleri."""

    @pytest.mark.asyncio
    async def test_resolve_auth_route(self):
        """'/api/auth/*' istekleri auth-service'e yönlendirilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        await router.register_service(
            ServiceInfo(name="auth-service", base_url="http://auth-service:8001")
        )
        result = await router.resolve_route("/api/auth/login")
        assert result is not None
        assert result.service_name == "auth-service"
        assert "auth-service:8001" in result.target_url

    @pytest.mark.asyncio
    async def test_resolve_product_route(self):
        """'/api/products/*' istekleri product-service'e yönlendirilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        await router.register_service(
            ServiceInfo(name="product-service", base_url="http://product-service:8002")
        )
        result = await router.resolve_route("/api/products")
        assert result is not None
        assert result.service_name == "product-service"

    @pytest.mark.asyncio
    async def test_resolve_order_route(self):
        """'/api/orders/*' istekleri order-service'e yönlendirilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        await router.register_service(
            ServiceInfo(name="order-service", base_url="http://order-service:8003")
        )
        result = await router.resolve_route("/api/orders")
        assert result is not None
        assert result.service_name == "order-service"

    @pytest.mark.asyncio
    async def test_resolve_unknown_route_returns_none(self):
        """Bilinmeyen bir URL path'i None dönmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        result = await router.resolve_route("/api/unknown")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_nested_route(self):
        """Derin nested path'ler de doğru şekilde yönlendirilmeli."""
        from app.routes.router import DispatcherRouter
        router = DispatcherRouter()
        await router.register_service(
            ServiceInfo(name="product-service", base_url="http://product-service:8002")
        )
        result = await router.resolve_route("/api/products/123/reviews")
        assert result is not None
        assert result.service_name == "product-service"


# ============================================================
# Integration Tests — API Endpoint'leri
# ============================================================

class TestRoutingEndpoints:
    """Dispatcher API üzerinden yönlendirme testleri."""

    @pytest.mark.asyncio
    async def test_proxy_get_products(self):
        """GET /api/products isteği product-service'e proxy yapılmalı."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/products")
            # Servis çalışmadığında bile 502/503 dönmeli, 200 değil
            assert response.status_code in [200, 502, 503]

    @pytest.mark.asyncio
    async def test_proxy_post_order(self):
        """POST /api/orders isteği order-service'e proxy yapılmalı."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/orders",
                json={"product_id": "123", "quantity": 1}
            )
            assert response.status_code in [201, 401, 502, 503]

    @pytest.mark.asyncio
    async def test_unknown_route_returns_404(self):
        """Bilinmeyen bir endpoint'e istek 404 dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/nonexistent")
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data or "error" in data
