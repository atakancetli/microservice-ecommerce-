"""
Edge Case testleri — Dispatcher.
Sınır değerler, beklenmeyen girişler ve hata senaryoları.
"""
import pytest
from app.services.rate_limiter import RateLimiterService
from app.services.retry_handler import CircuitBreaker, RetryHandler, CircuitState


class TestRateLimiterEdgeCases:
    """Rate Limiter sınır değer testleri."""

    @pytest.mark.asyncio
    async def test_exactly_at_limit(self):
        """Tam limit sınırında istek kontrolü."""
        limiter = RateLimiterService(max_requests=3, window_seconds=60)
        assert await limiter.is_allowed("client1") is True
        assert await limiter.is_allowed("client1") is True
        assert await limiter.is_allowed("client1") is True
        assert await limiter.is_allowed("client1") is False  # 4. istek

    @pytest.mark.asyncio
    async def test_different_clients_isolated(self):
        """Farklı istemciler birbirini etkilememeli."""
        limiter = RateLimiterService(max_requests=2, window_seconds=60)
        assert await limiter.is_allowed("clientA") is True
        assert await limiter.is_allowed("clientA") is True
        assert await limiter.is_allowed("clientA") is False
        assert await limiter.is_allowed("clientB") is True  # B etkilenmemeli

    @pytest.mark.asyncio
    async def test_remaining_count(self):
        """Kalan hak doğru hesaplanmalı."""
        limiter = RateLimiterService(max_requests=5, window_seconds=60)
        assert await limiter.get_remaining("new_client") == 5
        await limiter.is_allowed("new_client")
        assert await limiter.get_remaining("new_client") == 4

    @pytest.mark.asyncio
    async def test_empty_client_id(self):
        """Boş client ID çalışmalı."""
        limiter = RateLimiterService(max_requests=1, window_seconds=60)
        assert await limiter.is_allowed("") is True


class TestCircuitBreakerEdgeCases:
    """Circuit Breaker sınır değer testleri."""

    def test_initial_state_closed(self):
        """Başlangıç durumu CLOSED olmalı."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.get_state("new-service") == CircuitState.CLOSED

    def test_opens_after_threshold(self):
        """Eşik aşıldığında OPEN olmalı."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure("svc")
        cb.record_failure("svc")
        cb.record_failure("svc")
        assert cb.get_state("svc") == CircuitState.OPEN

    def test_is_allowed_when_closed(self):
        """CLOSED durumda istek geçmeli."""
        cb = CircuitBreaker()
        assert cb.is_allowed("svc") is True

    def test_is_not_allowed_when_open(self):
        """OPEN durumda istek engellenmeli."""
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure("svc")
        cb.record_failure("svc")
        assert cb.is_allowed("svc") is False

    def test_success_resets_failure_count(self):
        """Başarılı istek hata sayısını sıfırlamalı."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure("svc")
        cb.record_failure("svc")
        cb.record_success("svc")
        assert cb.get_state("svc") == CircuitState.CLOSED


class TestRetryHandlerEdgeCases:
    """Retry Handler sınır değer testleri."""

    def test_should_not_retry_4xx(self):
        """4xx hatalarında retry yapılmamalı."""
        handler = RetryHandler(max_retries=3)
        assert handler.should_retry(400, 0) is False
        assert handler.should_retry(401, 0) is False
        assert handler.should_retry(404, 0) is False

    def test_should_retry_5xx(self):
        """5xx hatalarında retry yapılmalı."""
        handler = RetryHandler(max_retries=3)
        assert handler.should_retry(500, 0) is True
        assert handler.should_retry(502, 0) is True
        assert handler.should_retry(503, 1) is True

    def test_should_retry_408_timeout(self):
        """408 Timeout'ta retry yapılmalı."""
        handler = RetryHandler(max_retries=3)
        assert handler.should_retry(408, 0) is True

    def test_max_retries_exceeded(self):
        """Max retry aşıldığında durdurulmalı."""
        handler = RetryHandler(max_retries=2)
        assert handler.should_retry(500, 0) is True
        assert handler.should_retry(500, 1) is True
        assert handler.should_retry(500, 2) is False

    def test_exponential_backoff(self):
        """Exponential backoff doğru hesaplanmalı."""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        assert handler.get_delay(0) == 0.1
        assert handler.get_delay(1) == 0.2
        assert handler.get_delay(2) == 0.4
