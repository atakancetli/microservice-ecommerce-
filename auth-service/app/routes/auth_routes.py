"""
Auth Routes — Auth Service API endpoint'leri.
RMM Seviye 2: Doğru HTTP metotları ve durum kodları.
"""
from fastapi import APIRouter, HTTPException, status

from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
)
async def register(user_data: UserCreate):
    """
    Yeni bir kullanıcı kaydeder.

    - **username**: Kullanıcı adı (min 3, max 50 karakter)
    - **email**: Benzersiz e-posta adresi
    - **password**: Şifre (min 6 karakter)

    Returns: 201 Created + kullanıcı bilgileri
    Errors: 409 Conflict (email zaten kayıtlı)
    """
    user = await AuthService.register(user_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu e-posta adresi zaten kayıtlı.",
        )

    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"],
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Kullanıcı girişi",
)
async def login(login_data: UserLogin):
    """
    Kullanıcı girişi yapar ve JWT token döner.

    - **email**: Kayıtlı e-posta adresi
    - **password**: Şifre

    Returns: 200 OK + JWT access token
    Errors: 401 Unauthorized (geçersiz credentials)
    """
    token_response = await AuthService.login(login_data)
    if token_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz e-posta veya şifre.",
        )

    return token_response


@router.get(
    "/users",
    response_model=list,
    summary="Tüm kullanıcıları listele",
)
async def list_users():
    """
    Tüm kayıtlı kullanıcıları listeler (admin endpoint).
    Şifre bilgisi yanıta dahil edilmez.
    """
    users = await AuthService.get_all_users()
    return [
        {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "created_at": user.get("created_at"),
        }
        for user in users
    ]


@router.get(
    "/me",
    summary="Mevcut kullanıcı profili",
)
async def get_current_user(x_user_id: str = None):
    """
    X-User-Id header'ından mevcut kullanıcının profilini döner.
    Gateway tarafından JWT çözümlendikten sonra çağrılır.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required.",
        )
    user = await AuthService.get_user_by_id(x_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı.",
        )
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "user"),
    }


@router.get("/health", summary="Auth Service sağlık kontrolü")
async def health():
    """Auth Service health check."""
    return {"status": "healthy", "service": "auth-service"}
