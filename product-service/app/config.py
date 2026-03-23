"""
Product Service konfigürasyon ayarları.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Product Service ortam değişkenleri."""

    MONGO_URL: str = "mongodb://product-mongo:27017"
    MONGO_DB: str = "product_db"

    class Config:
        env_file = ".env"


settings = Settings()
