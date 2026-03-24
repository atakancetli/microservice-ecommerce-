"""
Dispatcher soyut arayüzleri (Abstract Interfaces).
SOLID prensiplerinin Interface Segregation ve Dependency Inversion
ilkelerine uygun olarak tasarlanmıştır.

Tüm somut (concrete) sınıflar bu arayüzleri implemente edecektir.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# ============================================================
# Value Objects
# ============================================================

class LogLevel(Enum):
    """Log seviyesi enum'u."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class HttpMethod(Enum):
    """HTTP metot enum'u — RMM Seviye 2 uyumlu."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ServiceInfo:
    """Bir mikroservisin kayıt bilgileri."""
    name: str
    base_url: str
    health_endpoint: str = "/health"
    is_healthy: bool = True


@dataclass
class RouteResult:
    """Yönlendirme sonucu."""
    target_url: str
    service_name: str
    path: str


@dataclass
class LogEntry:
    """Bir log kaydı."""
    timestamp: datetime
    level: LogLevel
    message: str
    service: str
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AuthUser:
    """Kimliği doğrulanmış kullanıcı bilgisi."""
    user_id: str
    username: str
    email: str
    role: str = "user"


# ============================================================
# Abstract Interfaces
# ============================================================

class IRouter(ABC):
    """
    Yönlendirme arayüzü.
    Gelen istekleri URL yapısına göre ilgili mikroservise yönlendirir.
    """

    @abstractmethod
    async def register_service(self, service: ServiceInfo) -> None:
        """Bir mikroservisi servis kaydına ekler."""
        pass

    @abstractmethod
    async def unregister_service(self, service_name: str) -> None:
        """Bir mikroservisi servis kaydından çıkarır."""
        pass

    @abstractmethod
    async def resolve_route(self, path: str) -> Optional[RouteResult]:
        """
        URL path'ini analiz ederek hedef servisi belirler.
        Eşleşme bulunamazsa None döner.
        """
        pass

    @abstractmethod
    async def get_registered_services(self) -> List[ServiceInfo]:
        """Kayıtlı tüm servislerin listesini döner."""
        pass


class IAuthMiddleware(ABC):
    """
    Yetkilendirme middleware arayüzü.
    JWT token doğrulama ve yetki kontrolü yapar.
    """

    @abstractmethod
    async def authenticate(self, token: str) -> Optional[AuthUser]:
        """
        JWT token'ı doğrular ve kullanıcı bilgilerini döner.
        Geçersiz token durumunda None döner.
        """
        pass

    @abstractmethod
    async def authorize(self, user: AuthUser, resource: str, method: HttpMethod) -> bool:
        """
        Kullanıcının belirli bir kaynağa erişim yetkisini kontrol eder.
        Yetkili ise True, değilse False döner.
        """
        pass

    @abstractmethod
    async def create_token(self, user: AuthUser) -> str:
        """Kullanıcı için JWT token oluşturur."""
        pass

    @abstractmethod
    async def is_public_route(self, path: str) -> bool:
        """Verilen yolun public (auth gerektirmeyen) olup olmadığını kontrol eder."""
        pass


class IProxyService(ABC):
    """
    Proxy servis arayüzü.
    İstekleri hedef mikroservise iletir ve yanıtı döner.
    """

    @abstractmethod
    async def forward_request(
        self,
        method: str,
        target_url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        İsteği hedef URL'ye iletir.
        Returns: {"status_code": int, "body": Any, "headers": dict}
        """
        pass

    @abstractmethod
    async def health_check(self, service: ServiceInfo) -> bool:
        """Bir servisin sağlık durumunu kontrol eder."""
        pass


class ILogger(ABC):
    """
    Loglama arayüzü.
    Tüm trafik ve yönetici işlemlerini loglar.
    """

    @abstractmethod
    async def log(self, entry: LogEntry) -> None:
        """Bir log kaydı ekler."""
        pass

    @abstractmethod
    async def get_logs(
        self,
        level: Optional[LogLevel] = None,
        service: Optional[str] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """Filtrelere göre log kayıtlarını getirir."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Genel istatistikleri döner.
        Örn: toplam istek, hata oranı, ortalama yanıt süresi.
        """
        pass


class IRateLimiter(ABC):
    """
    Rate limiting arayüzü.
    Belirli bir süre içinde izin verilen maksimum istek sayısını kontrol eder.
    """

    @abstractmethod
    async def is_allowed(self, client_id: str) -> bool:
        """İstemcinin istek yapmasına izin verilip verilmediğini kontrol eder."""
        pass

    @abstractmethod
    async def get_remaining(self, client_id: str) -> int:
        """İstemcinin kalan istek hakkını döner."""
        pass
