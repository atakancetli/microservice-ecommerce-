"""
RequestLogger — İstek/yanıt loglama servisi.
ILogger arayüzünün somut implementasyonu.
SOLID: Single Responsibility — yalnızca log yönetimi.
"""
from typing import Dict, Any, List, Optional

from app.models.interfaces import ILogger, LogEntry, LogLevel


class RequestLogger(ILogger):
    """
    Tüm trafik ve yönetici işlemlerini loglar.
    In-memory depolama (production'da Redis'e geçirilecek).
    """

    def __init__(self):
        self._logs: List[LogEntry] = []

    async def log(self, entry: LogEntry) -> None:
        """Bir log kaydı ekler."""
        self._logs.append(entry)

    async def get_logs(
        self,
        level: Optional[LogLevel] = None,
        service: Optional[str] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """
        Filtrelere göre log kayıtlarını getirir.
        En son eklenen kayıtlar önce döner.
        """
        filtered = self._logs.copy()

        if level is not None:
            filtered = [log for log in filtered if log.level == level]

        if service is not None:
            filtered = [log for log in filtered if log.service == service]

        # Son kayıtlardan limit kadar döndür
        return filtered[-limit:]

    async def get_stats(self) -> Dict[str, Any]:
        """
        Genel istatistikleri döner:
        - total_requests: Toplam istek sayısı
        - error_rate: Hata oranı (4xx + 5xx)
        - avg_response_time_ms: Ortalama yanıt süresi
        """
        total = len(self._logs)

        # Hata sayısı (status_code >= 400)
        errors = len([
            log for log in self._logs
            if log.status_code is not None and log.status_code >= 400
        ])

        # Yanıt süreleri
        response_times = [
            log.response_time_ms
            for log in self._logs
            if log.response_time_ms is not None
        ]

        return {
            "total_requests": total,
            "error_rate": errors / total if total > 0 else 0.0,
            "avg_response_time_ms": (
                sum(response_times) / len(response_times)
                if response_times
                else 0.0
            ),
        }
