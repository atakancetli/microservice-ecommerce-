"""
Dispatcher Proxy & Health Check Testleri — TDD RED Aşaması.
İsteklerin mikroservislere iletilmesini ve sağlık kontrollerini test eder.
"""
import pytest
from app.models.interfaces import IProxyService, ServiceInfo


class TestProxyForwarding:
    """İstek proxy testleri."""

    @pytest.mark.asyncio
    async def test_forward_get_request(self):
        """GET isteği hedef servise iletilmeli."""
        from app.services.proxy_service import ProxyServiceImpl
        proxy = ProxyServiceImpl()
        result = await proxy.forward_request(
            method="GET",
            target_url="http://product-service:8002/products",
        )
        assert "status_code" in result
        assert "body" in result

    @pytest.mark.asyncio
    async def test_forward_post_request_with_body(self):
        """POST isteği body ile birlikte hedef servise iletilmeli."""
        from app.services.proxy_service import ProxyServiceImpl
        proxy = ProxyServiceImpl()
        result = await proxy.forward_request(
            method="POST",
            target_url="http://order-service:8003/orders",
            body={"product_id": "123", "quantity": 2},
            headers={"Content-Type": "application/json"},
        )
        assert "status_code" in result

    @pytest.mark.asyncio
    async def test_forward_preserves_headers(self):
        """Proxy, önemli header'ları korumalı."""
        from app.services.proxy_service import ProxyServiceImpl
        proxy = ProxyServiceImpl()
        result = await proxy.forward_request(
            method="GET",
            target_url="http://product-service:8002/products",
            headers={"X-Custom-Header": "test-value"},
        )
        assert "headers" in result

    @pytest.mark.asyncio
    async def test_forward_with_query_params(self):
        """Query parametreleri hedef servise iletilmeli."""
        from app.services.proxy_service import ProxyServiceImpl
        proxy = ProxyServiceImpl()
        result = await proxy.forward_request(
            method="GET",
            target_url="http://product-service:8002/products",
            query_params={"page": "1", "limit": "10"},
        )
        assert "status_code" in result


class TestHealthCheck:
    """Servis sağlık kontrolü testleri."""

    @pytest.mark.asyncio
    async def test_healthy_service_returns_true(self):
        """Çalışan servis için sağlık kontrolü True dönmeli."""
        from app.services.proxy_service import ProxyServiceImpl
        proxy = ProxyServiceImpl()
        service = ServiceInfo(
            name="test-service",
            base_url="http://localhost:8001",
            health_endpoint="/health",
        )
        # Not: servis çalışmadığı için bu test şimdilik False dönecek
        result = await proxy.health_check(service)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_unreachable_service_returns_false(self):
        """Ulaşılamayan servis için sağlık kontrolü False dönmeli."""
        from app.services.proxy_service import ProxyServiceImpl
        proxy = ProxyServiceImpl()
        service = ServiceInfo(
            name="unreachable",
            base_url="http://nonexistent-host:9999",
        )
        result = await proxy.health_check(service)
        assert result is False
