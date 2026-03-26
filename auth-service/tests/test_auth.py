"""
Auth Service — Unit & Integration testleri.
Kullanıcı kayıt, giriş ve token doğrulama testleri.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.auth_service import AuthService
from app.models.user import UserCreate, UserLogin


class TestPasswordHashing:
    """Şifre hashleme testleri."""

    def test_hash_password_returns_hash(self):
        """hash_password bcrypt hash döndürmeli."""
        hashed = AuthService.hash_password("test123")
        assert hashed != "test123"
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        """Doğru şifre verify edilmeli."""
        hashed = AuthService.hash_password("mypassword")
        assert AuthService.verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        """Yanlış şifre verify edilmemeli."""
        hashed = AuthService.hash_password("mypassword")
        assert AuthService.verify_password("wrongpassword", hashed) is False


class TestTokenCreation:
    """JWT token oluşturma testleri."""

    def test_create_token_returns_string(self):
        """Token string olarak dönmeli."""
        token = AuthService.create_access_token({
            "user_id": "123",
            "username": "test",
            "email": "test@test.com",
            "role": "user",
        })
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_has_three_parts(self):
        """JWT token 3 parça (header.payload.signature) içermeli."""
        token = AuthService.create_access_token({"user_id": "123"})
        parts = token.split(".")
        assert len(parts) == 3


class TestUserModel:
    """Kullanıcı model validasyon testleri."""

    def test_valid_user_create(self):
        """Geçerli kullanıcı kaydı oluşturulabilmeli."""
        user = UserCreate(
            username="testuser",
            email="test@test.com",
            password="password123",
        )
        assert user.username == "testuser"
        assert user.email == "test@test.com"

    def test_user_create_short_username_fails(self):
        """Kısa username reddedilmeli (min 3 karakter)."""
        with pytest.raises(Exception):
            UserCreate(username="ab", email="test@test.com", password="password123")

    def test_user_create_short_password_fails(self):
        """Kısa şifre reddedilmeli (min 6 karakter)."""
        with pytest.raises(Exception):
            UserCreate(username="testuser", email="test@test.com", password="12345")

    def test_valid_user_login(self):
        """Geçerli giriş verisi oluşturulabilmeli."""
        login = UserLogin(email="test@test.com", password="password123")
        assert login.email == "test@test.com"
