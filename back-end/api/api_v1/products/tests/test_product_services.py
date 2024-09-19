import pytest
from pydantic import ValidationError
from api.products.schemas import ProductCreate, ProductUpdate
from api.products.services import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
)


@pytest.mark.asyncio
class TestProductService:

    async def test_create_product(self, db_session):
        with pytest.raises(ValidationError):
            product_data = ProductCreate(
                name="newproduct",
                description="new description",
                price=20.0,
                category="new category",
                stock_quantity=100,
                points=10,
            )
        product_data = ProductCreate(
            name="newproduct",
            description="new description",
            price=20.0,
            category="category",
            stock_quantity=100,
            points=10,
        )
        product = await create_product(db_session, product_data)
        assert product.name == "newproduct"

    async def test_get_products(self, db_session, product_fixture):
        products = await get_products(db_session)
        assert len(products) >= 1

    async def test_get_product(self, db_session, product_fixture):
        product = await get_product(db_session, product_fixture.product_id)
        assert product.name == "Test Product"

    async def test_update_product(self, db_session, product_fixture):
        updated_data = ProductUpdate(name="updated product", price=25.0)
        product = await update_product(
            db_session, product_fixture, updated_data, partial=True
        )
        assert product.name == "updated product"
        assert product.price == 25.0

    async def test_delete_product(self, db_session, product_fixture):
        await delete_product(db_session, product_fixture.product_id)
        product = await get_product(db_session, product_fixture.product_id)
        assert product is None
