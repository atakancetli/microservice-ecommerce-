"""
Dispatcher Logging Testleri — TDD RED Aşaması.
Tüm trafik ve yönetici işlemlerinin loglanmasını test eder.
"""
import pytest
from datetime import datetime
from app.models.interfaces import ILogger, LogEntry, LogLevel


class TestLogCreation:
    """Log kaydı oluşturma testleri."""

    @pytest.mark.asyncio
    async def test_log_info_entry(self):
        """INFO seviyesinde log kaydı oluşturulabilmeli."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            message="GET /api/products",
            service="dispatcher",
            method="GET",
            path="/api/products",
            status_code=200,
            response_time_ms=45.2,
        )
        await logger.log(entry)
        logs = await logger.get_logs(limit=1)
        assert len(logs) == 1
        assert logs[0].message == "GET /api/products"

    @pytest.mark.asyncio
    async def test_log_error_entry(self):
        """ERROR seviyesinde log kaydı oluşturulabilmeli."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            message="Service unreachable: product-service",
            service="dispatcher",
            method="GET",
            path="/api/products",
            status_code=503,
        )
        await logger.log(entry)
        logs = await logger.get_logs(level=LogLevel.ERROR)
        assert len(logs) >= 1
        assert logs[0].level == LogLevel.ERROR

    @pytest.mark.asyncio
    async def test_log_with_metadata(self):
        """Metadata içeren log kaydı oluşturulabilmeli."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            message="Request forwarded",
            service="dispatcher",
            metadata={"target": "product-service", "client_ip": "192.168.1.1"},
        )
        await logger.log(entry)
        logs = await logger.get_logs(limit=1)
        assert logs[0].metadata is not None
        assert "target" in logs[0].metadata


class TestLogFiltering:
    """Log filtreleme testleri."""

    @pytest.mark.asyncio
    async def test_filter_by_level(self):
        """Log seviyesine göre filtreleme çalışmalı."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        # Farklı seviyelerde loglar ekle
        for level in [LogLevel.INFO, LogLevel.ERROR, LogLevel.WARNING]:
            await logger.log(LogEntry(
                timestamp=datetime.now(),
                level=level,
                message=f"Test {level.value}",
                service="dispatcher",
            ))
        error_logs = await logger.get_logs(level=LogLevel.ERROR)
        assert all(log.level == LogLevel.ERROR for log in error_logs)

    @pytest.mark.asyncio
    async def test_filter_by_service(self):
        """Servis adına göre filtreleme çalışmalı."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        await logger.log(LogEntry(
            timestamp=datetime.now(), level=LogLevel.INFO,
            message="Test", service="auth-service",
        ))
        await logger.log(LogEntry(
            timestamp=datetime.now(), level=LogLevel.INFO,
            message="Test", service="product-service",
        ))
        auth_logs = await logger.get_logs(service="auth-service")
        assert all(log.service == "auth-service" for log in auth_logs)

    @pytest.mark.asyncio
    async def test_limit_results(self):
        """Sonuç limiti doğru çalışmalı."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        for i in range(20):
            await logger.log(LogEntry(
                timestamp=datetime.now(), level=LogLevel.INFO,
                message=f"Log {i}", service="dispatcher",
            ))
        logs = await logger.get_logs(limit=5)
        assert len(logs) <= 5


class TestLogStats:
    """Log istatistik testleri."""

    @pytest.mark.asyncio
    async def test_get_stats_returns_total(self):
        """İstatistikler toplam istek sayısını içermeli."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        await logger.log(LogEntry(
            timestamp=datetime.now(), level=LogLevel.INFO,
            message="Test", service="dispatcher",
            status_code=200, response_time_ms=50.0,
        ))
        stats = await logger.get_stats()
        assert "total_requests" in stats
        assert stats["total_requests"] >= 1

    @pytest.mark.asyncio
    async def test_get_stats_returns_error_rate(self):
        """İstatistikler hata oranını içermeli."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        stats = await logger.get_stats()
        assert "error_rate" in stats

    @pytest.mark.asyncio
    async def test_get_stats_returns_avg_response_time(self):
        """İstatistikler ortalama yanıt süresini içermeli."""
        from app.services.log_service import RequestLogger
        logger = RequestLogger()
        await logger.log(LogEntry(
            timestamp=datetime.now(), level=LogLevel.INFO,
            message="Test", service="dispatcher",
            response_time_ms=100.0,
        ))
        await logger.log(LogEntry(
            timestamp=datetime.now(), level=LogLevel.INFO,
            message="Test 2", service="dispatcher",
            response_time_ms=200.0,
        ))
        stats = await logger.get_stats()
        assert "avg_response_time_ms" in stats
