import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import Product
from app.core.exceptions import (
    InvalidUuidError,
    ProductNameDuplicationError,
    ProductNotFoundError,
    InvalidSortFieldError,
    InvalidProductOrderError,
)
from app.api.api_v1.products.services import (
    get_products,
    get_product,
    search_products,
    create_product,
    bulk_create_product,
    update_product,
    delete_product,
)
from app.api.api_v1.products.schemas import (
    ProductCreate,
    ProductPartialUpdate,
    ProductUpdate,
    ProductBulkCreate, ProductTranslations,
)


@pytest.mark.asyncio
async def test_get_products(session: AsyncSession):
    """Test fetching products with pagination."""
    # Assuming products are already added in setup
    products = await get_products(session, limit=5, offset=0)

    assert len(products) <= 5
    assert all(isinstance(product, Product) for product in products)


@pytest.mark.asyncio
async def test_get_product(session: AsyncSession):
    """Test fetching a product by ID."""
    # Create a sample product first
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Test Product",
            product_description="A test product"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=10.99,
        category="Food",
        stock_quantity=100,
        image_src="test_image.png",
    )
    created_product = await create_product(session, product_data)

    # Fetch the product
    fetched_product = await get_product(session, created_product.product_id)

    assert fetched_product.product_id == created_product.product_id
    assert fetched_product.translations[0].product_name == "Test Product"
    assert fetched_product.translations[0].product_description == "A test product"
    assert fetched_product.translations[0].language_code == "en"
    assert fetched_product.price == 10.99
    assert fetched_product.category == "Food"
    assert fetched_product.stock_quantity == 100
    assert fetched_product.image_src == "test_image.png"

@pytest.mark.asyncio
async def test_get_product_not_found(session: AsyncSession):
    """Test fetching a non-existent product."""
    non_existent_product_id = uuid.uuid4()

    with pytest.raises(ProductNotFoundError):
        await get_product(session, non_existent_product_id)


@pytest.mark.asyncio
async def test_create_product(session: AsyncSession):
    """Test creating a new product."""
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name=f"New Product",
            product_description=f"A new product"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=12.99,
        category="Electronics",
        stock_quantity=50,
        image_src="new_image.png",
    )

    product = await create_product(session, product_data)

    assert product.translations[0].product_name == "New Product"
    assert product.price == 12.99
    assert product.category == "Electronics"


@pytest.mark.asyncio
async def test_create_product_duplicate_name(session: AsyncSession):
    """Test creating a product with a duplicate name."""
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Duplicate Product",
            product_description="A duplicate test product"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=19.99,
        category="Home",
        stock_quantity=10,
        image_src="duplicate_image.png",
    )

    # First product creation should succeed
    await create_product(session, product_data)

    # Second product with the same name should raise ProductNameDuplicationError
    with pytest.raises(ProductNameDuplicationError):
        await create_product(session, product_data)


@pytest.mark.asyncio
async def test_bulk_create_products(session: AsyncSession):
    """Test bulk creating products."""
    product_translations_1 = [
        ProductTranslations(
            language_code="en",
            product_name="Bulk Product 1",
            product_description="Bulk product description"
        )
    ]
    product_translations_2 = [
        ProductTranslations(
            language_code="en",
            product_name="Bulk Product 2",
            product_description="Another bulk product"
        )
    ]
    bulk_product_data = ProductBulkCreate(
        products=[
            ProductCreate(
                translations=product_translations_1,
                price=9.99,
                category="Food",
                stock_quantity=100,
                image_src="bulk1.png",
            ),
            ProductCreate(
                translations=product_translations_2,
                price=15.99,
                category="Electronics",
                stock_quantity=50,
                image_src="bulk2.png",
            ),
        ]
    )

    bulk_products = await bulk_create_product(session, bulk_product_data)

    assert len(bulk_products.products) == 2
    assert bulk_products.products[0].translations[0].product_name == "Bulk Product 1"


@pytest.mark.asyncio
async def test_bulk_create_products_duplicate(session: AsyncSession):
    """Test bulk creating products with a duplicate."""
    # First, create a product
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Existing Product",
            product_description="An existing product"
        )
    ]
    unique_product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="New Bulk Product",
            product_description="new Bulk Product"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=11.99,
        category="Home",
        stock_quantity=30,
        image_src="existing_image.png",
    )
    await create_product(session, product_data)

    # Now attempt to bulk create with a duplicate name
    bulk_product_data = ProductBulkCreate(
        products=[
            ProductCreate(
                translations=product_translations,
                price=19.99,
                category="Home",
                stock_quantity=10,
                image_src="duplicate.png",
            ),
            ProductCreate(
                translations=unique_product_translations,
                price=25.99,
                category="Electronics",
                stock_quantity=50,
                image_src="new_bulk.png",
            ),
        ]
    )

    with pytest.raises(ProductNameDuplicationError):
        await bulk_create_product(session, bulk_product_data)


@pytest.mark.asyncio
async def test_update_product(session: AsyncSession):
    """Test updating an existing product."""
    # Create a product first
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Product to Update",
            product_description="Product description"
        )
    ]

    product_data = ProductCreate(
        translations=product_translations,
        price=12.99,
        category="Toys",
        stock_quantity=30,
        image_src="update_image.png",
    )
    created_product = await create_product(session, product_data)

    product_translations_update = [
        ProductTranslations(
            language_code="en",
            product_name="Updated Product",
            product_description="Updated product description"
        )
    ]

    # Now update the product
    update_data = ProductUpdate(
        translations=product_translations_update,
        price=15.99,
        category="Games",
        stock_quantity=20,
        image_src="updated_image.png",
    )
    updated_product = await update_product(
        session, created_product.product_id, update_data
    )

    assert updated_product.translations[0].product_name == "Updated Product"
    assert updated_product.price == 15.99
    assert updated_product.category == "Games"


@pytest.mark.asyncio
async def test_delete_product(session: AsyncSession):
    """Test deleting a product."""
    # Create a product first
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Product to Delete",
            product_description="This product will be deleted"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=9.99,
        category="Food",
        stock_quantity=100,
        image_src="delete_image.png",
    )
    created_product = await create_product(session, product_data)

    # Now delete the product
    await delete_product(session, created_product.product_id)

    # Attempting to get the deleted product should raise ProductNotFoundError
    with pytest.raises(ProductNotFoundError):
        await get_product(session, created_product.product_id)


@pytest.mark.asyncio
async def test_search_products(session: AsyncSession):
    """Test searching products by category and name."""
    # Create a few products
    product_translations_1 = [
        ProductTranslations(
            language_code="en",
            product_name="Search Product 1",
            product_description="Product 1 description"
        ),
    ]
    product_translations_2 = [
        ProductTranslations(
            language_code="en",
            product_name="Search Product 2",
            product_description="Product 2 description"
        ),
    ]
    await create_product(
        session,
        ProductCreate(
            translations=product_translations_1,
            price=5.99,
            category="Food",
            stock_quantity=100,
            image_src="search1.png",
        ),
    )
    await create_product(
        session,
        ProductCreate(
            translations=product_translations_2,
            price=15.99,
            category="Electronics",
            stock_quantity=50,
            image_src="search2.png",
        ),
    )

    # Search by name
    products_by_name = await search_products(session, name="Search Product 1")
    assert len(products_by_name) == 1
    assert products_by_name[0].translations[0].product_name == "Search Product 1"

    # Search by category
    products_by_category = await search_products(session, category="Electronics")
    assert len(products_by_category) == 1
    assert products_by_category[0].category == "Electronics"


@pytest.mark.asyncio
async def test_search_products_invalid_sort_field(session: AsyncSession):
    """Test searching products with an invalid sort field."""
    with pytest.raises(InvalidSortFieldError):
        await search_products(session, sort_by="invalid_field")


@pytest.mark.asyncio
async def test_search_products_invalid_order_raises_exception(session: AsyncSession):
    """Test searching products with an invalid order parameter."""
    with pytest.raises(InvalidProductOrderError):
        await search_products(session, sort_by="price", order="invalid_order")


@pytest.mark.asyncio
async def test_get_products_pagination(session: AsyncSession):
    """Test fetching products with pagination and offsets."""

    # Create 6 products
    for i in range(6):
        product_translations = [
            ProductTranslations(
                language_code="en",
                product_name=f"Paginated Product {i}",
                product_description=f"Description for product {i}"
            )
        ]
        await create_product(
            session,
            ProductCreate(
                translations=product_translations,
                price=5.99 + i,
                category="Toys",
                stock_quantity=10 + i,
                image_src=f"image_{i}.png",
            ),
        )

    # Fetch the first 5 products (with explicit ordering)
    products_page_1 = await search_products(session, limit=5, offset=0, sort_by="name")
    assert len(products_page_1) == 5

    # Fetch the next set (remaining product)
    products_page_2 = await search_products(session, limit=5, offset=5, sort_by="name")
    assert len(products_page_2) == 1

    # Ensure pagination works and products are fetched in correct order
    assert products_page_1[0].translations[0].product_name == "Paginated Product 0"
    assert products_page_2[0].translations[0].product_name == "Paginated Product 5"


@pytest.mark.asyncio
async def test_update_product_partial(session: AsyncSession):
    """Test partially updating a product."""
    # Create a product first
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Product for Partial Update",
            product_description="This product will be partially updated"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=20.99,
        category="Books",
        stock_quantity=150,
        image_src="partial_update.png",
    )
    created_product = await create_product(session, product_data)

    # Now partially update the product (only change the name)
    partial_update_data = ProductPartialUpdate(
        translations=[{
            "language_code": "en",
            "product_name": "Partially Updated Product"}],
    )
    updated_product = await update_product(
        session, created_product.product_id, partial_update_data, partial=True
    )

    assert updated_product.translations[0].product_name == "Partially Updated Product"
    assert (
        updated_product.translations[0].product_description == "This product will be partially updated"
    )  # Unchanged
    assert updated_product.price == 20.99  # Unchanged


@pytest.mark.asyncio
async def test_delete_non_existent_product_raises_exception(session: AsyncSession):
    """Test attempting to delete a non-existent product."""
    non_existent_product_id = uuid.uuid4()

    # Attempting to delete a non-existent product should raise ProductNotFoundError
    with pytest.raises(ProductNotFoundError):
        await delete_product(session, non_existent_product_id)


@pytest.mark.asyncio
async def test_get_products_no_results(session: AsyncSession):
    """Test fetching products when none exist."""
    products = await get_products(session)
    assert products == []


@pytest.mark.asyncio
async def test_search_products_invalid_order(session: AsyncSession):
    """Test searching products with an invalid order parameter."""
    # Create a valid product first
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Valid Product",
            product_description="Valid product"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=20.99,
        category="Books",
        stock_quantity=50,
        image_src="valid_product.png",
    )
    await create_product(session, product_data)

    # Now test an invalid order
    with pytest.raises(InvalidProductOrderError):
        await search_products(session, sort_by="price", order="invalid_order")


@pytest.mark.asyncio
async def test_bulk_create_duplicate_names_in_same_request(session: AsyncSession):
    """Test bulk creating products with duplicate names in the same request."""
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Duplicate Bulk Product",
            product_description="Duplicate X"
        )
    ]
    bulk_product_data = ProductBulkCreate(
        products=[
            ProductCreate(
                translations=product_translations,
                price=9.99,
                category="Food",
                stock_quantity=100,
                image_src="bulk1.png",
            ),
            ProductCreate(
                translations=product_translations,
                price=15.99,
                category="Electronics",
                stock_quantity=50,
                image_src="bulk2.png",
            ),
        ]
    )

    with pytest.raises(ProductNameDuplicationError):
        await bulk_create_product(session, bulk_product_data)


@pytest.mark.asyncio
async def test_update_product_partial_update(session: AsyncSession):
    """Test partial updates to a product."""
    # Create a product
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Partial Update Product",
            product_description="Original description"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=12.99,
        category="Toys",
        stock_quantity=30,
        image_src="original_image.png",
    )
    created_product = await create_product(session, product_data)

    # Now update only the price
    partial_update_data = ProductPartialUpdate(price=25.99)  # type: ignore
    updated_product = await update_product(
        session, created_product.product_id, partial_update_data, partial=True
    )

    assert updated_product.price == 25.99
    assert updated_product.translations[0].product_name == "Partial Update Product"  # Unchanged


@pytest.mark.asyncio
async def test_delete_product_and_check_exclusion_from_listings(session: AsyncSession):
    """Test soft deleting a product and ensuring it is excluded from product listings."""
    # Create a product
    product_translations = [
        ProductTranslations(
            language_code="en",
            product_name="Product to be Deleted",
            product_description="This product will be deleted"
        )
    ]
    product_data = ProductCreate(
        translations=product_translations,
        price=10.99,
        category="Electronics",
        stock_quantity=50,
        image_src="to_delete.png",
    )
    created_product = await create_product(session, product_data)

    # Soft delete the product
    await delete_product(session, created_product.product_id)

    # Ensure it is excluded from listings
    products = await get_products(session)
    assert not any(p.product_id == created_product.product_id for p in products)

    # Ensure fetching the deleted product raises an error
    with pytest.raises(ProductNotFoundError):
        await get_product(session, created_product.product_id)


@pytest.mark.asyncio
async def test_get_product_with_invalid_uuid(session: AsyncSession):
    """Test fetching a product with an invalid UUID."""
    invalid_product_id = "invalid-uuid-string"
    with pytest.raises(InvalidUuidError):
        await get_product(session, invalid_product_id)  # type: ignore


@pytest.mark.asyncio
async def test_delete_product_with_invalid_uuid(session: AsyncSession):
    """Test deleting a product with an invalid UUID."""
    invalid_product_id = "invalid-uuid-string"
    with pytest.raises(InvalidUuidError):
        await delete_product(session, invalid_product_id)  # type: ignore


@pytest.mark.asyncio
async def test_delete_non_existent_product(session: AsyncSession):
    """Test attempting to delete a product that doesn't exist."""
    non_existent_product_id = uuid.uuid4()

    # Attempting to delete a non-existent product should raise ProductNotFoundError
    with pytest.raises(ProductNotFoundError):
        await delete_product(session, non_existent_product_id)
