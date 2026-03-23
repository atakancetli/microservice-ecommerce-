"""
Order Service konfigürasyon ayarları.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Order Service ortam değişkenleri."""

    MONGO_URL: str = "mongodb://order-mongo:27017"
    MONGO_DB: str = "order_db"
    PRODUCT_SERVICE_URL: str = "http://product-service:8002"

    class Config:
        env_file = ".env"


settings = Settings()
