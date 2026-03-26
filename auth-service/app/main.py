"""
Auth Service - Kimlik doğrulama ve yetkilendirme.
Kullanıcı kaydı, girişi ve JWT token yönetimi.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.services.database import Database
from app.routes.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü: DB bağlantı yönetimi."""
    # Startup — MongoDB'ye bağlan
    await Database.connect()
    print(f"🔐 Auth Service starting on port 8001")
    yield
    # Shutdown — MongoDB bağlantısını kapat
    await Database.disconnect()
    print("🛑 Auth Service shutting down")


app = FastAPI(
    title="Auth Service",
    description="Kullanıcı kaydı, girişi ve JWT token yönetimi.",
    version="1.0.0",
    lifespan=lifespan,
)

# Auth route'larını ekle
app.include_router(auth_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Auth Service sağlık kontrolü."""
    return {"status": "healthy", "service": "auth-service"}
