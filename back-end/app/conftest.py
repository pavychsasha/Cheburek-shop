from typing import Any, AsyncGenerator
from urllib import response
from app.api.api_v1.products.schemas import ProductBulkCreate, ProductCreate
from app.api.api_v1.products.services import bulk_create_product, get_products
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from app.core.models import Base, User
from app.core.config import settings
from app.main import app as main_app
from app.core.models import SQLDatabaseHelper, MongoDbHelper, sql_db_helper


# Override settings to use test databases
settings.db.url = settings.db.test_url
settings.mongo_db.url = settings.mongo_db.test_url
settings.mongo_db.database_name = settings.mongo_db.test_database_name


@pytest.fixture(scope="function")
async def test_sql_db():
    """Fixture to create a test instance of SQLDatabaseHelper."""
    test_sql_db_helper = SQLDatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )
    return test_sql_db_helper


@pytest.fixture(scope="function")
async def test_mongo_db() -> MongoDbHelper:
    """Fixture to create a test instance of MongoDbHelper."""
    test_mongo_db_helper = MongoDbHelper(
        db_url=settings.mongo_db.test_url,
        db_name=settings.mongo_db.test_database_name,
    )
    return test_mongo_db_helper


@pytest.fixture(scope="function", autouse=True)
async def reset_databases(
    test_sql_db: SQLDatabaseHelper,
    test_mongo_db: MongoDbHelper,
):
    """Fixture to drop and recreate all databases before each test."""
    async with test_sql_db.engine.begin() as conn:
        # Drop and recreate SQL database tables
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await test_mongo_db.connect()

    yield  # Proceed with the test function

    # Dispose of the engine after the test
    await test_sql_db.dispose()
    await test_mongo_db.dispose()


@pytest.fixture(scope="function")
async def session(test_sql_db: SQLDatabaseHelper) -> AsyncGenerator[AsyncSession, Any]:
    """
    Fixture to provide an AsyncSession for database interactions in tests.
    The session will be closed after each test.
    """
    async with test_sql_db.session_factory() as session:
        yield session
        await session.close()


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("reset_databases")
async def client(
    test_sql_db: SQLDatabaseHelper,
):
    """Set up a FastAPI client for testing."""

    # Override session dependency in FastAPI with the test session
    main_app.dependency_overrides[sql_db_helper.session_dependency] = (
        test_sql_db.session_dependency
    )

    async with AsyncClient(
        app=main_app,
        base_url="http://testserver",
    ) as ac:
        yield ac

    # Clear dependency overrides after the test
    main_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def products(session: AsyncSession):
    products_lst = [
        {
            "name": "Potato pie",
            "description": "Pie with tender potatoes",
            "price": 20,
            "category": "Patties",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
            "product_id": "244f9cdd-1f65-451b-a9e8-2248ce7b0e63",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Cheburek with chicken, cheese and mushrooms",
            "description": "Cheburek with chicken, cheese and mushrooms",
            "price": 65,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
            "product_id": "31b03a13-1be7-41c1-83fa-e7560ef18e47",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Cheburek with meat and cheese",
            "description": "Cheburek with meat and cheese",
            "price": 60,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
            "product_id": "36d465c6-7d4e-45e1-af30-7d75d42828d1",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Sprite 0.5l",
            "description": "Sprite refreshing drink 0.5l",
            "price": 30,
            "category": "Beverages",
            "stock_quantity": 300,
            "image_src": "https://i.imgur.com/l7RFgRd.png",
            "product_id": "4b5ac79a-b788-4b17-bd3d-1b21697e6424",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Cheburek with chicken and cheese",
            "description": "Cheburek with chicken and cheese",
            "price": 60,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
            "product_id": "794affd7-cf3b-4304-b983-6bc1b607dbc1",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Cheburek with meat, cheese and mushrooms",
            "description": "Cheburek with meat, cheese and mushrooms",
            "price": 65,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
            "product_id": "7d55ecf9-e7c2-495b-9d6a-81f12680414a",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Nuggets",
            "description": "Juicy nuggets",
            "price": 25,
            "category": "Other",
            "stock_quantity": 150,
            "image_src": "https://i.imgur.com/UAYLcz3.png",
            "product_id": "8f5da484-6cc8-4665-ac4d-89470b49636f",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Pie with potatoes and mushrooms",
            "description": "Pie with potatoes and mushrooms",
            "price": 25,
            "category": "Patties",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
            "product_id": "96592016-0be1-4978-9594-ec9d9dc7d391",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Coca-Cola 0.5L",
            "description": "Refreshing drink Coca-Cola 0.5l",
            "price": 30,
            "category": "Beverages",
            "stock_quantity": 300,
            "image_src": "https://i.imgur.com/ym0F0Lg.png",
            "product_id": "9cf64564-b38a-4bb3-a5ce-ceb58667f664",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
        {
            "name": "Cheburek with meat",
            "description": "Cheburek with delicious meat",
            "price": 55,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
            "product_id": "9e71884a-5345-41b4-b3cd-00ca5f003fa8",
            "created_at": "2024-09-26T00:14:28.554784",
            "updated_at": "2024-09-26T00:14:28.554784",
        },
    ]
    product_bulk = ProductBulkCreate(
        products=[ProductCreate(**product_obj) for product_obj in products_lst]
    )
    await bulk_create_product(session=session, products_in=product_bulk)
    return await get_products(session=session)
