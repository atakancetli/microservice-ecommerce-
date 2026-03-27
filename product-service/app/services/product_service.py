"""
ProductService — Ürün CRUD iş mantığı.
SOLID: Single Responsibility — sadece ürün operasyonları.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from bson import ObjectId

from app.services.database import Database
from app.models.product import ProductCreate, ProductUpdate


class ProductService:
    """
    Ürün CRUD operasyonları.
    MongoDB ile async iletişim kurar.
    """

    COLLECTION = "products"

    @classmethod
    async def create(cls, product_data: ProductCreate) -> Dict[str, Any]:
        """
        Yeni ürün oluşturur.
        Returns: Oluşturulan ürün document'ı.
        """
        collection = Database.get_collection(cls.COLLECTION)
        doc = {
            "name": product_data.name,
            "description": product_data.description,
            "price": product_data.price,
            "stock": product_data.stock,
            "category": product_data.category,
            "image_url": product_data.image_url,
            "created_at": datetime.utcnow(),
            "updated_at": None,
        }
        result = await collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @classmethod
    async def get_all(
        cls,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Ürün listesini getirir (pagination + filtre).
        """
        collection = Database.get_collection(cls.COLLECTION)
        query = {}
        if category:
            query["category"] = category

        cursor = collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @classmethod
    async def get_by_id(cls, product_id: str) -> Optional[Dict[str, Any]]:
        """Ürünü ID ile getirir."""
        collection = Database.get_collection(cls.COLLECTION)
        try:
            return await collection.find_one({"_id": ObjectId(product_id)})
        except Exception:
            return None

    @classmethod
    async def update(
        cls, product_id: str, update_data: ProductUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Ürünü günceller (partial update).
        Sadece gönderilen alanlar güncellenir.
        """
        collection = Database.get_collection(cls.COLLECTION)

        # None olmayan alanları al
        update_fields = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }
        if not update_fields:
            return await cls.get_by_id(product_id)

        update_fields["updated_at"] = datetime.utcnow()

        try:
            result = await collection.find_one_and_update(
                {"_id": ObjectId(product_id)},
                {"$set": update_fields},
                return_document=True,
            )
            return result
        except Exception:
            return None

    @classmethod
    async def delete(cls, product_id: str) -> bool:
        """Ürünü siler. Başarılıysa True döner."""
        collection = Database.get_collection(cls.COLLECTION)
        try:
            result = await collection.delete_one({"_id": ObjectId(product_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @classmethod
    async def search(cls, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Ürün adı veya açıklamasında arama yapar."""
        collection = Database.get_collection(cls.COLLECTION)
        search_filter = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ]
        }
        cursor = collection.find(search_filter).limit(limit)
        return await cursor.to_list(length=limit)
