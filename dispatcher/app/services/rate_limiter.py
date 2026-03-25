"""
RateLimiterService — İstek hız sınırlama servisi.
IRateLimiter arayüzünün somut implementasyonu.
SOLID: Single Responsibility — yalnızca rate limiting.
"""
import time
from typing import Dict, List

from app.models.interfaces import IRateLimiter


class RateLimiterService(IRateLimiter):
    """
    Sliding window algoritması ile rate limiting.
    Her istemci için belirli bir zaman penceresi içinde
    izin verilen maksimum istek sayısını kontrol eder.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}

    async def is_allowed(self, client_id: str) -> bool:
        """
        İstemcinin istek yapmasına izin verilip verilmediğini kontrol eder.
        Sliding window içinde max_requests'i aşmamışsa True döner.
        """
        now = time.time()

        if client_id not in self._requests:
            self._requests[client_id] = []

        # Pencere dışındaki eski istekleri temizle
        self._requests[client_id] = [
            t for t in self._requests[client_id]
            if now - t < self._window_seconds
        ]

        # Limit kontrolü
        if len(self._requests[client_id]) >= self._max_requests:
            return False

        # İsteği kaydet
        self._requests[client_id].append(now)
        return True

    async def get_remaining(self, client_id: str) -> int:
        """
        İstemcinin kalan istek hakkını döner.
        """
        now = time.time()

        if client_id not in self._requests:
            return self._max_requests

        # Pencere içindeki aktif istekleri say
        active = [
            t for t in self._requests[client_id]
            if now - t < self._window_seconds
        ]

        return self._max_requests - len(active)
