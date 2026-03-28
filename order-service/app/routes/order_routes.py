"""
Order Routes — Order Service API endpoint'leri.
RMM Seviye 2: Doğru HTTP metotları ve durum kodları.
"""
from fastapi import APIRouter, HTTPException, status, Request, Query
from typing import List

from app.models.order import OrderCreate, OrderResponse, OrderStatus
from app.services.order_service import OrderService


router = APIRouter(prefix="/orders", tags=["Orders"])


def _to_response(doc: dict) -> OrderResponse:
    """MongoDB document'ını OrderResponse'a dönüştürür."""
    return OrderResponse(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        items=doc["items"],
        total_price=doc["total_price"],
        status=doc["status"],
        shipping_address=doc["shipping_address"],
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni sipariş oluştur",
)
async def create_order(request: Request, order_data: OrderCreate):
    """
    Yeni bir sipariş oluşturur.
    X-User-Id header'ından kullanıcı bilgisi alınır.
    """
    user_id = request.headers.get("X-User-Id", "anonymous")
    
    # Sipariş oluştur
    doc = await OrderService.create_order(user_id, order_data)
    return _to_response(doc)


@router.get(
    "",
    response_model=List[OrderResponse],
    summary="Kullanıcı siparişlerini listele",
)
async def list_orders(request: Request):
    """Kullanıcının tüm geçmiş siparişlerini getirir."""
    user_id = request.headers.get("X-User-Id", "anonymous")
    orders = await OrderService.get_user_orders(user_id)
    return [_to_response(doc) for doc in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Sipariş detayı",
)
async def get_order(order_id: str):
    """Sipariş detayını getirir."""
    doc = await OrderService.get_order_by_id(order_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sipariş bulunamadı: {order_id}"
        )
    return _to_response(doc)


@router.patch(
    "/{order_id}/status",
    summary="Sipariş durumu güncelle",
)
async def update_order_status(order_id: str, status: OrderStatus):
    """Sipariş durumunu günceller (admin/system)."""
    success = await OrderService.update_status(order_id, status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sipariş bulunamadı veya güncellenemedi."
        )
    return {"message": "Sipariş durumu güncellendi.", "status": status}
