"""
Product Service — Unit testleri.
Ürün model validasyonu ve CRUD operasyon testleri.
"""
import pytest
from app.models.product import ProductCreate, ProductUpdate, ProductResponse


class TestProductModel:
    """Ürün model validasyon testleri."""

    def test_valid_product_create(self):
        """Geçerli ürün oluşturulabilmeli."""
        product = ProductCreate(
            name="Test Ürünü",
            description="Test açıklaması",
            price=99.99,
            stock=10,
            category="electronics",
        )
        assert product.name == "Test Ürünü"
        assert product.price == 99.99
        assert product.stock == 10

    def test_product_create_min_name(self):
        """Ürün adı min 2 karakter olmalı."""
        with pytest.raises(Exception):
            ProductCreate(name="a", price=10.0)

    def test_product_create_negative_price_fails(self):
        """Negatif fiyat reddedilmeli."""
        with pytest.raises(Exception):
            ProductCreate(name="Test", price=-5.0)

    def test_product_create_negative_stock_fails(self):
        """Negatif stok reddedilmeli."""
        with pytest.raises(Exception):
            ProductCreate(name="Test", price=10.0, stock=-1)

    def test_product_create_defaults(self):
        """Varsayılan değerler doğru olmalı."""
        product = ProductCreate(name="Test", price=10.0)
        assert product.stock == 0
        assert product.category == "general"
        assert product.description == ""

    def test_product_update_partial(self):
        """Kısmi güncelleme çalışmalı (sadece belirli alanlar)."""
        update = ProductUpdate(price=199.99)
        assert update.price == 199.99
        assert update.name is None
        assert update.stock is None

    def test_product_update_empty(self):
        """Boş güncelleme kabul edilmeli."""
        update = ProductUpdate()
        assert update.name is None
        assert update.price is None


class TestProductResponse:
    """Ürün yanıt şeması testleri."""

    def test_response_has_all_fields(self):
        """Yanıt tüm alanları içermeli."""
        from datetime import datetime
        response = ProductResponse(
            id="abc123",
            name="Test",
            description="Açıklama",
            price=99.99,
            stock=5,
            category="electronics",
            created_at=datetime.now(),
        )
        assert response.id == "abc123"
        assert response.price == 99.99
        assert response.updated_at is None
