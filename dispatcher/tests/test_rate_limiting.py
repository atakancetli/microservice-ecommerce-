"""
Dispatcher Rate Limiting Testleri — TDD RED Aşaması.
Yoğun istek trafiğinde rate limiting mekanizmasını test eder.
"""
import pytest
from app.models.interfaces import IRateLimiter


class TestRateLimiting:
    """Rate limiter testleri."""

    @pytest.mark.asyncio
    async def test_first_request_is_allowed(self):
        """İlk istek kabul edilmeli."""
        from app.services.rate_limiter import RateLimiterService
        limiter = RateLimiterService(max_requests=10, window_seconds=60)
        assert await limiter.is_allowed("client1") is True

    @pytest.mark.asyncio
    async def test_within_limit_is_allowed(self):
        """Limit dahilindeki istekler kabul edilmeli."""
        from app.services.rate_limiter import RateLimiterService
        limiter = RateLimiterService(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert await limiter.is_allowed("client1") is True

    @pytest.mark.asyncio
    async def test_over_limit_is_rejected(self):
        """Limiti aşan istekler reddedilmeli."""
        from app.services.rate_limiter import RateLimiterService
        limiter = RateLimiterService(max_requests=3, window_seconds=60)
        for _ in range(3):
            await limiter.is_allowed("client1")
        assert await limiter.is_allowed("client1") is False

    @pytest.mark.asyncio
    async def test_different_clients_independent(self):
        """Farklı istemcilerin limitleri bağımsız olmalı."""
        from app.services.rate_limiter import RateLimiterService
        limiter = RateLimiterService(max_requests=2, window_seconds=60)
        await limiter.is_allowed("client1")
        await limiter.is_allowed("client1")
        # client1 limiti doldu ama client2 hala yapabilmeli
        assert await limiter.is_allowed("client2") is True

    @pytest.mark.asyncio
    async def test_get_remaining_requests(self):
        """Kalan istek hakkı doğru dönmeli."""
        from app.services.rate_limiter import RateLimiterService
        limiter = RateLimiterService(max_requests=10, window_seconds=60)
        await limiter.is_allowed("client1")
        await limiter.is_allowed("client1")
        remaining = await limiter.get_remaining("client1")
        assert remaining == 8
