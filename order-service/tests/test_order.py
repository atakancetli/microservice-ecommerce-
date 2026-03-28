"""
Order Service — Unit & Integration testleri.
Sipariş oluşturma ve model validasyon testleri (TDD RED).
"""
import pytest
from app.models.order import OrderCreate, OrderItem, OrderStatus, OrderResponse
from datetime import datetime


class TestOrderModel:
    """Sipariş model validasyon testleri."""

    def test_valid_order_create(self):
        """Geçerli sipariş oluşturma verisi kabul edilmeli."""
        item = OrderItem(product_id="prod-1", quantity=2, price_at_order=100.0)
        order = OrderCreate(
            items=[item],
            shipping_address="Test Mah. No:1, İstanbul"
        )
        assert len(order.items) == 1
        assert order.items[0].product_id == "prod-1"

    def test_order_no_items_fails(self):
        """Boş ürün listesi reddedilmeli."""
        with pytest.raises(Exception):
            OrderCreate(items=[], shipping_address="Test Address")

    def test_order_short_address_fails(self):
        """Kısa adres reddedilmeli (min 10 karakter)."""
        item = OrderItem(product_id="prod-1", quantity=1, price_at_order=50.0)
        with pytest.raises(Exception):
            OrderCreate(items=[item], shipping_address="Kısa")


class TestOrderResponse:
    """Sipariş yanıt şeması testleri."""

    def test_response_fields(self):
        """Yanıt tüm zorunlu alanları içermeli."""
        item = OrderItem(product_id="p-1", quantity=1, price_at_order=10.0)
        response = OrderResponse(
            id="ord-123",
            user_id="user-456",
            items=[item],
            total_price=10.0,
            status=OrderStatus.PENDING,
            shipping_address="Uzun Test Adresi 123",
            created_at=datetime.utcnow()
        )
        assert response.id == "ord-123"
        assert response.status == "pending"


class TestOrderServiceInterService:
    """Servisler arası iletişim ve stok kontrolü testleri (RED)."""

    def test_stock_verification_mock(self):
        """Ürün servisinden stok kontrolü mock (RED)."""
        # Bu test service implementasyonu bittiğinde eklenecek, 
        # şimdilik TDD placeholder.
        assert True

