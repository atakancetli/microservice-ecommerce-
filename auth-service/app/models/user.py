"""
User modeli — Auth Service.
Kullanıcı kayıt, giriş ve token yanıt şemaları.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Kullanıcı kayıt isteği."""
    username: str = Field(..., min_length=3, max_length=50, description="Kullanıcı adı")
    email: str = Field(..., description="E-posta adresi")
    password: str = Field(..., min_length=6, description="Şifre (min 6 karakter)")


class UserLogin(BaseModel):
    """Kullanıcı giriş isteği."""
    email: str = Field(..., description="E-posta adresi")
    password: str = Field(..., description="Şifre")


class UserResponse(BaseModel):
    """Kullanıcı bilgi yanıtı."""
    id: str
    username: str
    email: str
    role: str = "user"
    created_at: datetime


class UserInDB(BaseModel):
    """Veritabanındaki kullanıcı temsili."""
    username: str
    email: str
    hashed_password: str
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TokenResponse(BaseModel):
    """JWT token yanıtı."""
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
