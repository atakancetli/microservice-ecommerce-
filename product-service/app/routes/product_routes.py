"""
Product Routes — Product Service API endpoint'leri.
RMM Seviye 2: Doğru HTTP metotları ve durum kodları.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.models.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["Products"])


def _to_response(doc: dict) -> ProductResponse:
    """MongoDB document'ını ProductResponse'a dönüştürür."""
    return ProductResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description", ""),
        price=doc["price"],
        stock=doc.get("stock", 0),
        category=doc.get("category", "general"),
        image_url=doc.get("image_url"),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni ürün ekle",
)
async def create_product(product_data: ProductCreate):
    """
    Yeni bir ürün oluşturur.

    - **name**: Ürün adı (min 2 karakter)
    - **price**: Fiyat (> 0)
    - **stock**: Stok miktarı (>= 0)
    - **category**: Kategori (varsayılan: general)

    Returns: 201 Created + ürün bilgileri
    """
    doc = await ProductService.create(product_data)
    return _to_response(doc)


@router.get(
    "",
    response_model=list[ProductResponse],
    summary="Ürün listesi",
)
async def list_products(
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(20, ge=1, le=100, description="Döndürülecek kayıt sayısı"),
    category: Optional[str] = Query(None, description="Kategori filtresi"),
):
    """
    Ürün listesini getirir (pagination + filtre desteği).

    Returns: 200 OK + ürün listesi
    """
    products = await ProductService.get_all(skip=skip, limit=limit, category=category)
    return [_to_response(doc) for doc in products]


@router.get(
    "/search",
    response_model=list[ProductResponse],
    summary="Ürün ara",
)
async def search_products(
    q: str = Query(..., min_length=1, description="Arama sorgusu"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Ürün adı veya açıklamasında arama yapar.

    Returns: 200 OK + eşleşen ürünler
    """
    products = await ProductService.search(query=q, limit=limit)
    return [_to_response(doc) for doc in products]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Ürün detayı",
)
async def get_product(product_id: str):
    """
    Belirli bir ürünün detaylarını getirir.

    Returns: 200 OK + ürün bilgileri
    Errors: 404 Not Found
    """
    doc = await ProductService.get_by_id(product_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ürün bulunamadı: {product_id}",
        )
    return _to_response(doc)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Ürün güncelle",
)
async def update_product(product_id: str, update_data: ProductUpdate):
    """
    Ürün bilgilerini günceller (partial update).
    Sadece gönderilen alanlar güncellenir.

    Returns: 200 OK + güncellenmiş ürün
    Errors: 404 Not Found
    """
    doc = await ProductService.update(product_id, update_data)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ürün bulunamadı: {product_id}",
        )
    return _to_response(doc)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ürün sil",
)
async def delete_product(product_id: str):
    """
    Ürünü siler.

    Returns: 204 No Content
    Errors: 404 Not Found
    """
    success = await ProductService.delete(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ürün bulunamadı: {product_id}",
        )


@router.get(
    "/stats/summary",
    summary="Ürün istatistikleri",
)
async def product_stats():
    """
    Toplam ürün sayısı, kategori dağılımı ve fiyat aralığı.
    Dashboard ve monitoring için kullanılır.
    """
    products = await ProductService.get_all(skip=0, limit=10000)
    if not products:
        return {"total": 0, "categories": {}, "avg_price": 0}

    categories = {}
    total_price = 0
    for p in products:
        cat = p.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        total_price += p.get("price", 0)

    return {
        "total": len(products),
        "categories": categories,
        "avg_price": round(total_price / len(products), 2),
        "total_stock": sum(p.get("stock", 0) for p in products),
    }
