"""
Auth Service - Kimlik doğrulama ve yetkilendirme.
Kullanıcı kaydı, girişi ve JWT token yönetimi.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma işlemleri."""
    print(f"🔐 Auth Service starting on port 8001")
    print(f"📦 MongoDB: {settings.MONGO_URL}/{settings.MONGO_DB}")
    yield
    print("🛑 Auth Service shutting down")


app = FastAPI(
    title="Auth Service",
    description="Kullanıcı kaydı, girişi ve JWT token yönetimi.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Auth Service sağlık kontrolü."""
    return {"status": "healthy", "service": "auth-service"}
