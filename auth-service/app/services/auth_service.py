"""
AuthService — Kimlik doğrulama iş mantığı.
SOLID: Single Responsibility — sadece auth operasyonları.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from passlib.context import CryptContext
from jose import jwt, JWTError

from app.config import settings
from app.services.database import Database
from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse


class AuthService:
    """
    Kullanıcı kayıt, giriş ve token yönetimi.
    bcrypt ile şifre hashleme, JWT ile token oluşturma.
    """

    # bcrypt password hashing context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Şifreyi bcrypt ile hashler."""
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Düz metin şifreyi hash ile karşılaştırır."""
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: Dict[str, Any]) -> str:
        """JWT access token oluşturur."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @classmethod
    async def register(cls, user_data: UserCreate) -> Optional[Dict[str, Any]]:
        """
        Yeni kullanıcı kaydı.
        Returns: Kaydedilen kullanıcı dict'i veya None (email zaten kayıtlı).
        """
        collection = Database.get_collection("users")

        # Email kontrolü
        existing = await collection.find_one({"email": user_data.email})
        if existing:
            return None

        # Kullanıcıyı oluştur
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": cls.hash_password(user_data.password),
            "role": "user",
            "created_at": datetime.utcnow(),
        }

        result = await collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        return user_doc

    @classmethod
    async def login(cls, login_data: UserLogin) -> Optional[TokenResponse]:
        """
        Kullanıcı girişi.
        Returns: TokenResponse veya None (geçersiz credentials).
        """
        collection = Database.get_collection("users")

        # Kullanıcıyı bul
        user = await collection.find_one({"email": login_data.email})
        if not user:
            return None

        # Şifre doğrula
        if not cls.verify_password(login_data.password, user["hashed_password"]):
            return None

        # Token oluştur
        token = cls.create_access_token({
            "user_id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user"),
        })

        user_response = UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            role=user.get("role", "user"),
            created_at=user["created_at"],
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_response,
        )

    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcıyı ID ile getirir."""
        from bson import ObjectId
        collection = Database.get_collection("users")
        return await collection.find_one({"_id": ObjectId(user_id)})

    @classmethod
    async def get_all_users(cls) -> list:
        """Tüm kullanıcıları listeler (admin için)."""
        collection = Database.get_collection("users")
        cursor = collection.find({}, {"hashed_password": 0})
        return await cursor.to_list(length=100)
