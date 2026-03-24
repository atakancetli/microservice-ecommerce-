"""
Dispatcher Auth Middleware Testleri — TDD RED Aşaması.
JWT token doğrulama ve yetkilendirme kontrollerini test eder.
Henüz implementasyon yapılmadığı için tüm testler FAIL olmalıdır.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.interfaces import IAuthMiddleware, AuthUser, HttpMethod


# ============================================================
# Unit Tests — AuthMiddleware Sınıfı
# ============================================================

class TestTokenAuthentication:
    """JWT token doğrulama testleri."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        """Geçerli bir JWT token ile kullanıcı bilgisi dönmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        user = AuthUser(
            user_id="user123", username="testuser",
            email="test@test.com", role="user"
        )
        token = await auth.create_token(user)
        result = await auth.authenticate(token)
        assert result is not None
        assert result.user_id == "user123"
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_invalid_token_returns_none(self):
        """Geçersiz bir token ile None dönmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        result = await auth.authenticate("invalid.token.here")
        assert result is None

    @pytest.mark.asyncio
    async def test_expired_token_returns_none(self):
        """Süresi dolmuş token ile None dönmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        # Expired token simülasyonu
        result = await auth.authenticate("expired.token.value")
        assert result is None

    @pytest.mark.asyncio
    async def test_empty_token_returns_none(self):
        """Boş token ile None dönmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        result = await auth.authenticate("")
        assert result is None


class TestAuthorization:
    """Yetkilendirme kontrol testleri."""

    @pytest.mark.asyncio
    async def test_user_can_access_products(self):
        """Normal kullanıcı ürünleri görüntüleyebilmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        user = AuthUser(
            user_id="user1", username="testuser",
            email="test@test.com", role="user"
        )
        assert await auth.authorize(user, "/api/products", HttpMethod.GET) is True

    @pytest.mark.asyncio
    async def test_user_can_create_order(self):
        """Normal kullanıcı sipariş oluşturabilmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        user = AuthUser(
            user_id="user1", username="testuser",
            email="test@test.com", role="user"
        )
        assert await auth.authorize(user, "/api/orders", HttpMethod.POST) is True

    @pytest.mark.asyncio
    async def test_user_cannot_delete_products(self):
        """Normal kullanıcı ürün silemememeli (sadece admin)."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        user = AuthUser(
            user_id="user1", username="testuser",
            email="test@test.com", role="user"
        )
        assert await auth.authorize(user, "/api/products", HttpMethod.DELETE) is False

    @pytest.mark.asyncio
    async def test_admin_can_delete_products(self):
        """Admin kullanıcı ürün silebilmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        admin = AuthUser(
            user_id="admin1", username="adminuser",
            email="admin@test.com", role="admin"
        )
        assert await auth.authorize(admin, "/api/products", HttpMethod.DELETE) is True


class TestPublicRoutes:
    """Public (auth gerektirmeyen) yol testleri."""

    @pytest.mark.asyncio
    async def test_health_is_public(self):
        """'/health' endpoint'i auth gerektirmemeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        assert await auth.is_public_route("/health") is True

    @pytest.mark.asyncio
    async def test_login_is_public(self):
        """'/api/auth/login' endpoint'i auth gerektirmemeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        assert await auth.is_public_route("/api/auth/login") is True

    @pytest.mark.asyncio
    async def test_register_is_public(self):
        """'/api/auth/register' endpoint'i auth gerektirmemeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        assert await auth.is_public_route("/api/auth/register") is True

    @pytest.mark.asyncio
    async def test_products_is_not_public(self):
        """'/api/products' endpoint'i auth gerektirmeli."""
        from app.middleware.auth_middleware import AuthMiddlewareService
        auth = AuthMiddlewareService()
        assert await auth.is_public_route("/api/products") is False


# ============================================================
# Integration Tests — Middleware API Testleri
# ============================================================

class TestAuthMiddlewareIntegration:
    """Dispatcher API üzerinden auth middleware testleri."""

    @pytest.mark.asyncio
    async def test_request_without_token_returns_401(self):
        """Token olmadan yapılan istek 401 Unauthorized dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/products")
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_request_with_invalid_token_returns_401(self):
        """Geçersiz token ile yapılan istek 401 dönmeli."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/products",
                headers={"Authorization": "Bearer invalid.token"}
            )
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_public_route_without_token_works(self):
        """Health endpoint'i token olmadan da çalışmalı."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
