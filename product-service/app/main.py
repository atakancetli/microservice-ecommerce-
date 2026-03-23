"""
Product Service - Ürün yönetimi.
Ürün ekleme, listeleme, güncelleme ve silme işlemleri.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma işlemleri."""
    print(f"📦 Product Service starting on port 8002")
    print(f"📦 MongoDB: {settings.MONGO_URL}/{settings.MONGO_DB}")
    yield
    print("🛑 Product Service shutting down")


app = FastAPI(
    title="Product Service",
    description="Ürün ekleme, listeleme, güncelleme ve silme.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Product Service sağlık kontrolü."""
    return {"status": "healthy", "service": "product-service"}
