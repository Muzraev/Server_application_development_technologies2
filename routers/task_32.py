from fastapi import APIRouter

from errors import AppNotFound, BAD_REQUEST_DOC, NOT_FOUND_DOC
from models.product import Product, ProductSearchRequest
from storage import sample_products

router = APIRouter(prefix="/task-3-2", tags=["Задание 3.2"])


@router.post(
    "/products/search",
    response_model=list[Product],
    summary="Поиск товаров",
    responses={400: BAD_REQUEST_DOC, 404: NOT_FOUND_DOC},
)
async def search_products(data: ProductSearchRequest):
    keyword_lower = data.keyword.strip().lower()
    category_lower = data.category.strip().lower() if data.category is not None else None

    results = []

    for product in sample_products:
        product_name = product["name"].lower()
        product_category = product["category"].lower()

        if keyword_lower in product_name:
            if category_lower is None or category_lower == product_category:
                results.append(product)

    if not results:
        raise AppNotFound("Товары по вашему запросу не найдены.")

    return results[: data.limit]


@router.get(
    "/product/{product_id}",
    response_model=Product,
    summary="Получить товар по ID",
    responses={400: BAD_REQUEST_DOC, 404: NOT_FOUND_DOC},
)
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product

    raise AppNotFound("Товар с таким product_id не найден.")