"""
Database katmanı — Order Service.
MongoDB bağlantı yönetimi (motor async driver).
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class Database:
    """MongoDB bağlantı yöneticisi (Singleton)."""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls) -> None:
        """MongoDB'ye bağlan."""
        cls.client = AsyncIOMotorClient(settings.MONGO_URL)
        cls.db = cls.client[settings.MONGO_DB]
        print(f"✅ Order DB connected: {settings.MONGO_URL}/{settings.MONGO_DB}")

    @classmethod
    async def disconnect(cls) -> None:
        """MongoDB bağlantısını kapat."""
        if cls.client:
            cls.client.close()

    @classmethod
    def get_collection(cls, name: str):
        """Belirli bir koleksiyonu döner."""
        if cls.db is None:
            raise RuntimeError("Database not connected.")
        return cls.db[name]
