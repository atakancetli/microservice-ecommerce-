"""
Order Service - Sipariş yönetimi.
Sipariş oluşturma, listeleme, güncelleme ve iptal işlemleri.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma işlemleri."""
    print(f"🛒 Order Service starting on port 8003")
    print(f"📦 MongoDB: {settings.MONGO_URL}/{settings.MONGO_DB}")
    yield
    print("🛑 Order Service shutting down")


app = FastAPI(
    title="Order Service",
    description="Sipariş oluşturma, listeleme, güncelleme ve iptal.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Order Service sağlık kontrolü."""
    return {"status": "healthy", "service": "order-service"}
