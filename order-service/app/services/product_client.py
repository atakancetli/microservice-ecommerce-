"""
ProductServiceClient — Product Service ile iletişim kuran istemci.
Sipariş öncesi stok ve ürün varlığı kontrolü yapar.
"""
import httpx
from app.config import settings

class ProductServiceClient:
    """
    Product Service'e HTTP istekleri atar.
    Docker internal network üzerinden erişir: http://product-service:8002
    """
    
    BASE_URL = settings.PRODUCT_SERVICE_URL or "http://product-service:8002"

    @classmethod
    async def get_product(cls, product_id: str) -> dict:
        """
        Ürün detaylarını getirir.
        Returns: Ürün dict veya None if 404.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{cls.BASE_URL}/products/{product_id}", timeout=5.0)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"❌ Error calling Product Service: {e}")
                return None

    @classmethod
    async def check_stocks(cls, items: list) -> bool:
        """
        Siparişteki her ürünün stokta olup olmadığını kontrol eder.
        """
        for item in items:
            product = await cls.get_product(item.product_id)
            if not product:
                return False
            if product.get("stock", 0) < item.quantity:
                return False
        return True
