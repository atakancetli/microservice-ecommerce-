"""
Order Service - Sipariş yönetimi.
Sipariş oluşturma, listeleme, güncelleme ve iptal işlemleri.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.services.database import Database
from app.routes.order_routes import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma işlemleri."""
    await Database.connect()
    print(f"🛒 Order Service starting on port 8003")
    yield
    await Database.disconnect()
    print("🛑 Order Service shutting down")


app = FastAPI(
    title="Order Service",
    description="Sipariş oluşturma, listeleme, güncelleme ve iptal.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(order_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Order Service sağlık kontrolü."""
    return {"status": "healthy", "service": "order-service"}
