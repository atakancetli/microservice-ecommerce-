"""
Dispatcher Error Handling Testleri — TDD RED Aşaması.
HTTP hata kodlarının doğru dönülmesini test eder.
Her zaman 200 OK dönüp JSON'da error flag koyma yaklaşımı KULLANILMAMALIDIR.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


class TestHttpErrorCodes:
    """HTTP durum kodlarının doğruluğu testleri."""

    @pytest.mark.asyncio
    async def test_not_found_returns_404(self):
        """Var olmayan bir kaynak 404 Not Found dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/nonexistent-resource")
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            # 200 OK + {"error": true} OLMAMALI
            assert response.status_code != 200

    @pytest.mark.asyncio
    async def test_method_not_allowed_returns_405(self):
        """İzin verilmeyen HTTP metodu 405 Method Not Allowed dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/health")
            assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_bad_request_returns_400(self):
        """Geçersiz request body 400 Bad Request dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/orders",
                content="invalid json{{{",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code in [400, 401, 422]

    @pytest.mark.asyncio
    async def test_unauthorized_returns_401(self):
        """Token olmayan istek 401 Unauthorized dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/products")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_forbidden_returns_403(self):
        """Yetkisiz işlem 403 Forbidden dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Normal kullanıcı admin endpoint'ine erişim
            response = await client.delete(
                "/api/products/1",
                headers={"Authorization": "Bearer user-token"}
            )
            assert response.status_code in [401, 403]


class TestServiceUnavailable:
    """Servis erişilemezliği testleri."""

    @pytest.mark.asyncio
    async def test_unreachable_service_returns_503(self):
        """Ulaşılamayan servise istek 503 Service Unavailable dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # auth-service çalışmıyorken
            response = await client.post(
                "/api/auth/login",
                json={"email": "test@test.com", "password": "pass"}
            )
            # Servis çalışmadığında 502 Bad Gateway veya 503 dönmeli
            assert response.status_code in [502, 503]

    @pytest.mark.asyncio
    async def test_timeout_returns_504(self):
        """Zaman aşımı durumunda 504 Gateway Timeout dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Timeout simülasyonu
            response = await client.get(
                "/api/products",
                headers={"X-Test-Simulate-Timeout": "true"}
            )
            assert response.status_code in [504, 502, 503]


class TestErrorResponseFormat:
    """Hata yanıt formatı testleri."""

    @pytest.mark.asyncio
    async def test_error_response_has_detail(self):
        """Hata yanıtları 'detail' alanı içermeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/unknown")
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert isinstance(data["detail"], str)
            assert len(data["detail"]) > 0

    @pytest.mark.asyncio
    async def test_error_response_has_correct_content_type(self):
        """Hata yanıtları application/json content-type ile dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/unknown")
            assert "application/json" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_never_returns_200_for_errors(self):
        """Hata durumlarında asla 200 OK dönülmemeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Var olmayan endpoint
            response = await client.get("/api/nonexistent")
            assert response.status_code != 200

            # Yetkisiz erişim
            response = await client.get("/api/products")
            assert response.status_code != 200
