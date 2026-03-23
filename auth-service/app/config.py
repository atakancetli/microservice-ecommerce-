"""
Auth Service konfigürasyon ayarları.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Auth Service ortam değişkenleri."""

    MONGO_URL: str = "mongodb://auth-mongo:27017"
    MONGO_DB: str = "auth_db"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
