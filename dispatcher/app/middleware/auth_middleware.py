"""
AuthMiddlewareService — JWT doğrulama ve yetkilendirme.
IAuthMiddleware arayüzünün somut implementasyonu.
SOLID: Open/Closed — yeni roller eklenebilir, mevcut kod değişmez.
"""
from typing import Optional, Set
from datetime import datetime, timedelta

from jose import jwt, JWTError

from app.models.interfaces import IAuthMiddleware, AuthUser, HttpMethod
from app.config import settings


class AuthMiddlewareService(IAuthMiddleware):
    """
    JWT token doğrulama ve rol tabanlı yetkilendirme servisi.
    Merkezi auth kontrol noktası — tüm yetkilendirme burada yapılır.
    """

    # Auth gerektirmeyen public endpoint'ler
    PUBLIC_ROUTES: Set[str] = {
        "/health",
        "/api/auth/login",
        "/api/auth/register",
        "/metrics",
    }

    # Sadece admin'lerin kullanabileceği HTTP metotları (kaynak bazlı)
    ADMIN_ONLY_OPERATIONS = {
        HttpMethod.DELETE,
    }

    async def create_token(self, user: AuthUser) -> str:
        """
        Kullanıcı bilgilerinden JWT token oluşturur.
        Token içeriği: user_id, username, email, role, exp.
        """
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        }
        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    async def authenticate(self, token: str) -> Optional[AuthUser]:
        """
        JWT token'ı doğrular ve kullanıcı bilgilerini döner.
        Geçersiz/süresi dolmuş token → None döner.
        """
        if not token:
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return AuthUser(
                user_id=payload["user_id"],
                username=payload["username"],
                email=payload["email"],
                role=payload.get("role", "user"),
            )
        except JWTError:
            return None
        except (KeyError, TypeError):
            return None

    async def authorize(
        self, user: AuthUser, resource: str, method: HttpMethod
    ) -> bool:
        """
        Kullanıcının belirli bir kaynağa erişim yetkisini kontrol eder.
        Admin: tüm işlemler.
        User: DELETE hariç tüm işlemler.
        """
        if user.role == "admin":
            return True

        if method in self.ADMIN_ONLY_OPERATIONS:
            return False

        return True

    async def is_public_route(self, path: str) -> bool:
        """
        Verilen yolun public (auth gerektirmeyen) olup olmadığını kontrol eder.
        Public: /health, /api/auth/login, /api/auth/register, /metrics
        """
        return path in self.PUBLIC_ROUTES
