"""
Order modelleri — Order Service.
Sipariş ve Sipariş Kalemi (OrderItem) şemaları.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Sipariş durumları."""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"


class OrderItem(BaseModel):
    """Sipariş içindeki her bir ürün."""
    product_id: str = Field(..., description="Ürün ID")
    quantity: int = Field(..., gt=0, description="Adet")
    price_at_order: float = Field(..., gt=0, description="Sipariş anındaki fiyat")


class OrderCreate(BaseModel):
    """Sipariş oluşturma isteği."""
    items: List[OrderItem] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=10)


class OrderResponse(BaseModel):
    """Sipariş yanıt şeması."""
    id: str
    user_id: str
    items: List[OrderItem]
    total_price: float
    status: OrderStatus
    shipping_address: str
    created_at: datetime
    updated_at: Optional[datetime] = None
