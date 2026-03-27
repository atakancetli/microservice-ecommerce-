"""
Product Service - Ürün yönetimi.
Ürün CRUD operasyonları ve arama.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.services.database import Database
from app.routes.product_routes import router as product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü: DB bağlantı yönetimi."""
    await Database.connect()
    print(f"📦 Product Service starting on port {settings.PORT}")
    yield
    await Database.disconnect()
    print("🛑 Product Service shutting down")


app = FastAPI(
    title="Product Service",
    description="Ürün yönetimi: CRUD, arama ve filtreleme.",
    version="1.0.0",
    lifespan=lifespan,
)

# Product route'larını ekle
app.include_router(product_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Product Service sağlık kontrolü."""
    return {"status": "healthy", "service": "product-service"}
