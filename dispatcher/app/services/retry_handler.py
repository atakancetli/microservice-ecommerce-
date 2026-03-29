"""
Retry Mechanism — Dispatcher.
Başarısız upstream isteklerini otomatik olarak tekrar dener.
Circuit Breaker pattern'i ile birlikte çalışır.
"""
import time
from typing import Dict, Any
from enum import Enum


class CircuitState(str, Enum):
    """Circuit Breaker durumları."""
    CLOSED = "closed"       # Normal çalışma
    OPEN = "open"          # Servis devre dışı
    HALF_OPEN = "half_open"  # Test modu


class CircuitBreaker:
    """
    Circuit Breaker Pattern.
    Bir servis sürekli hata verirse, bir süre istekleri almayı reddeder (OPEN).
    Belirli bir süre sonra tekrar dener (HALF_OPEN).
    Başarılı olursa CLOSED'a döner.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2,
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold

        self._failure_count: Dict[str, int] = {}
        self._success_count: Dict[str, int] = {}
        self._state: Dict[str, CircuitState] = {}
        self._last_failure_time: Dict[str, float] = {}

    def get_state(self, service: str) -> CircuitState:
        """Servisin mevcut durumunu döner."""
        if service not in self._state:
            return CircuitState.CLOSED

        state = self._state[service]

        # OPEN durumunda timeout kontrolü
        if state == CircuitState.OPEN:
            elapsed = time.time() - self._last_failure_time.get(service, 0)
            if elapsed >= self._recovery_timeout:
                self._state[service] = CircuitState.HALF_OPEN
                return CircuitState.HALF_OPEN

        return state

    def record_success(self, service: str) -> None:
        """Başarılı istek kaydı."""
        state = self.get_state(service)

        if state == CircuitState.HALF_OPEN:
            self._success_count[service] = self._success_count.get(service, 0) + 1
            if self._success_count[service] >= self._success_threshold:
                self._state[service] = CircuitState.CLOSED
                self._failure_count[service] = 0
                self._success_count[service] = 0
        else:
            self._failure_count[service] = 0

    def record_failure(self, service: str) -> None:
        """Başarısız istek kaydı."""
        self._failure_count[service] = self._failure_count.get(service, 0) + 1
        self._last_failure_time[service] = time.time()

        if self._failure_count[service] >= self._failure_threshold:
            self._state[service] = CircuitState.OPEN
            self._success_count[service] = 0

    def is_allowed(self, service: str) -> bool:
        """İstek yapılmasına izin verilip verilmediğini kontrol eder."""
        state = self.get_state(service)
        return state != CircuitState.OPEN

    def get_all_states(self) -> Dict[str, str]:
        """Tüm servislerin durumlarını döner."""
        return {
            service: self.get_state(service).value
            for service in self._state
        }


class RetryHandler:
    """
    Retry mechanism with exponential backoff.
    Başarısız istekleri artan bekleme süreleriyle tekrar dener.
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 0.1):
        self._max_retries = max_retries
        self._base_delay = base_delay

    @property
    def max_retries(self) -> int:
        return self._max_retries

    def get_delay(self, attempt: int) -> float:
        """Exponential backoff ile bekleme süresi hesaplar."""
        return self._base_delay * (2 ** attempt)

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """
        İsteğin tekrar denenip denenmeyeceğini belirler.
        Yalnızca 5xx hataları ve timeout'lar için retry yapılır.
        """
        if attempt >= self._max_retries:
            return False
        # 5xx server errors ve 408 timeout → retry
        return status_code >= 500 or status_code == 408
