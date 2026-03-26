"""
Dependency Injection Container — Dispatcher.
Tüm servis bağımlılıklarını merkezi olarak yönetir.
SOLID: Dependency Inversion — üst modüller soyutlamalara bağımlıdır.
"""
from app.models.interfaces import IRouter, IAuthMiddleware, IProxyService, ILogger, IRateLimiter
from app.routes.router import DispatcherRouter
from app.middleware.auth_middleware import AuthMiddlewareService
from app.services.proxy_service import ProxyServiceImpl
from app.services.log_service import RequestLogger
from app.services.rate_limiter import RateLimiterService


class ServiceContainer:
    """
    Singleton servis konteyneri.
    Tüm Dispatcher bileşenlerini merkezi olarak oluşturur ve yönetir.
    SOLID - Dependency Inversion: Somut sınıflar yerine interface'ler üzerinden erişim.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._router: IRouter = DispatcherRouter()
        self._auth: IAuthMiddleware = AuthMiddlewareService()
        self._proxy: IProxyService = ProxyServiceImpl()
        self._logger: ILogger = RequestLogger()
        self._rate_limiter: IRateLimiter = RateLimiterService(
            max_requests=100, window_seconds=60
        )
        self._initialized = True

    @property
    def router(self) -> IRouter:
        return self._router

    @property
    def auth(self) -> IAuthMiddleware:
        return self._auth

    @property
    def proxy(self) -> IProxyService:
        return self._proxy

    @property
    def logger(self) -> ILogger:
        return self._logger

    @property
    def rate_limiter(self) -> IRateLimiter:
        return self._rate_limiter


# Global container instance
container = ServiceContainer()
