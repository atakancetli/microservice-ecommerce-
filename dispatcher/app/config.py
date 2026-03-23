"""
Dispatcher konfigürasyon ayarları.
Tüm ortam değişkenleri burada merkezi olarak yönetilir.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Dispatcher için ortam değişkenleri."""

    # Server
    PORT: int = 8080

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Mikroservis URL'leri
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    PRODUCT_SERVICE_URL: str = "http://product-service:8002"
    ORDER_SERVICE_URL: str = "http://order-service:8003"

    # Güvenlik
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
