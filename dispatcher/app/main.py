"""
Dispatcher (API Gateway) - Mikroservis Mimarisi
Tüm dış isteklerin tek giriş noktası.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma işlemleri."""
    # Startup
    print(f"🚀 Dispatcher starting on port {settings.PORT}")
    print(f"📡 Auth Service: {settings.AUTH_SERVICE_URL}")
    print(f"📡 Product Service: {settings.PRODUCT_SERVICE_URL}")
    print(f"📡 Order Service: {settings.ORDER_SERVICE_URL}")
    yield
    # Shutdown
    print("🛑 Dispatcher shutting down")


app = FastAPI(
    title="Dispatcher - API Gateway",
    description="Mikroservis mimarisinin tek giriş noktası. "
                "Tüm istekleri ilgili servislere yönlendirir.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Dispatcher sağlık kontrolü."""
    return {"status": "healthy", "service": "dispatcher"}
