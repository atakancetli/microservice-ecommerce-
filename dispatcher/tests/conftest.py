"""
Dispatcher test yapılandırması.
Tüm test dosyaları için ortak fixture'lar.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Test client fixture — Dispatcher API'yi test etmek için."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
