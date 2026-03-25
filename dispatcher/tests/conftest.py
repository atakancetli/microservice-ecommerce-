"""
Dispatcher test yapılandırması.
Tüm test dosyaları için ortak fixture'lar.
TDD GREEN aşaması — testlerin çalışabilmesi için gerekli kurulum.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, router_service, auth_service
from app.models.interfaces import ServiceInfo, AuthUser


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Test client fixture — Dispatcher API'yi test etmek için."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token():
    """Geçerli bir JWT token oluşturur (test amaçlı)."""
    user = AuthUser(
        user_id="test-user-1",
        username="testuser",
        email="test@test.com",
        role="user",
    )
    token = await auth_service.create_token(user)
    return token


@pytest.fixture
async def admin_token():
    """Admin JWT token oluşturur (test amaçlı)."""
    admin = AuthUser(
        user_id="admin-1",
        username="adminuser",
        email="admin@test.com",
        role="admin",
    )
    token = await auth_service.create_token(admin)
    return token
