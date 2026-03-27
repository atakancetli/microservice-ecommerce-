"""
Product modeli — Product Service.
Ürün CRUD işlemleri için Pydantic şemaları.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Yeni ürün ekleme isteği."""
    name: str = Field(..., min_length=2, max_length=200, description="Ürün adı")
    description: str = Field("", max_length=2000, description="Ürün açıklaması")
    price: float = Field(..., gt=0, description="Fiyat (TL)")
    stock: int = Field(0, ge=0, description="Stok miktarı")
    category: str = Field("general", description="Ürün kategorisi")
    image_url: Optional[str] = Field(None, description="Ürün görseli URL")


class ProductUpdate(BaseModel):
    """Ürün güncelleme isteği (partial update)."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    """Ürün yanıt şeması."""
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
