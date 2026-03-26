"""
Database katmanı — Auth Service.
MongoDB bağlantı yönetimi (motor async driver).
SOLID: Single Responsibility — yalnızca veritabanı bağlantısı.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class Database:
    """
    MongoDB bağlantı yöneticisi (Singleton pattern).
    motor kütüphanesi ile async bağlantı sağlar.
    """

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls) -> None:
        """MongoDB'ye bağlan."""
        cls.client = AsyncIOMotorClient(settings.MONGO_URL)
        cls.db = cls.client[settings.MONGO_DB]

        # users koleksiyonu için unique index oluştur
        users = cls.db["users"]
        await users.create_index("email", unique=True)

        print(f"✅ Connected to MongoDB: {settings.MONGO_URL}/{settings.MONGO_DB}")

    @classmethod
    async def disconnect(cls) -> None:
        """MongoDB bağlantısını kapat."""
        if cls.client:
            cls.client.close()
            print("🔌 MongoDB connection closed")

    @classmethod
    def get_collection(cls, name: str):
        """Belirli bir koleksiyonu döner."""
        if cls.db is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls.db[name]
