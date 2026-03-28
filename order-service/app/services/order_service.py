"""
OrderService — Sipariş iş mantığı.
SOLID: Single Responsibility — sadece sipariş operasyonları.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.models.order import OrderCreate, OrderStatus
from app.services.database import Database


class OrderService:
    """
    Sipariş oluşturma, sorgulama ve güncelleme.
    MongoDB ile async iletişim kurar.
    """

    COLLECTION = "orders"

    @classmethod
    async def create_order(
        cls, user_id: str, order_data: OrderCreate
    ) -> Dict[str, Any]:
        """
        Yeni bir sipariş oluşturur.
        Total price item'lardan hesaplanır.
        """
        collection = Database.get_collection(cls.COLLECTION)
        
        # Toplam fiyatı hesapla
        total_price = sum(item.quantity * item.price_at_order for item in order_data.items)

        order_doc = {
            "user_id": user_id,
            "items": [item.model_dump() for item in order_data.items],
            "total_price": total_price,
            "status": OrderStatus.PENDING,
            "shipping_address": order_data.shipping_address,
            "created_at": datetime.utcnow(),
            "updated_at": None,
        }

        result = await collection.insert_one(order_doc)
        order_doc["_id"] = result.inserted_id
        return order_doc

    @classmethod
    async def get_user_orders(cls, user_id: str) -> List[Dict[str, Any]]:
        """Kullanıcının tüm siparişlerini getirir."""
        collection = Database.get_collection(cls.COLLECTION)
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=100)

    @classmethod
    async def get_order_by_id(cls, order_id: str) -> Optional[Dict[str, Any]]:
        """Siparişi ID ile getirir."""
        collection = Database.get_collection(cls.COLLECTION)
        try:
            return await collection.find_one({"_id": ObjectId(order_id)})
        except Exception:
            return None

    @classmethod
    async def update_status(cls, order_id: str, status: OrderStatus) -> bool:
        """Sipariş durumunu günceller."""
        collection = Database.get_collection(cls.COLLECTION)
        try:
            result = await collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": status, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
