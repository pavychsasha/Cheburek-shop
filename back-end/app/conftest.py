import asyncio
from http.client import responses
from typing import Any, AsyncGenerator

from app.core.config import settings  # noqa

# Override settings to use test databases
settings.db.url = settings.db.test_url  # noqa
settings.mongo_db.url = settings.mongo_db.test_url  # noqa
settings.mongo_db.database_name = settings.mongo_db.test_database_name  # noqa
settings.cookie_transport_settings.cookie_secure = False  # noqa

from app.core.schemas.products import ProductBulkCreate, ProductCreate
from app.api.v1.products.services import ProductsService
import pytest
from sqlalchemy import update, text
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.core.models import Base, User, Address, Order
from app.main import app as main_app
from app.core.models import (
    SQLDatabaseHelper,
    MongoDbHelper,
    sql_db_helper,
    redis_db_helper,
)


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
        # Temporarily disable foreign key checks
        await conn.execute(text("SET session_replication_role = 'replica';"))

        # Drop all tables without dependency checks
        await conn.run_sync(Base.metadata.drop_all)

        # Re-enable foreign key checks
        await conn.execute(text("SET session_replication_role = 'origin';"))

        # Recreate all tables
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
        await session.rollback()
        await session.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_test_redis():
    # Adjust singleton Redis instance to use the test database
    redis_db_helper.db = 2
    await redis_db_helper.connect()  # Reinitialize connection to use the test DB
    yield
    await redis_db_helper.dispose()  # Ensure closure after tests


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("reset_databases")
async def client(test_sql_db: SQLDatabaseHelper):
    """Set up a FastAPI client for testing."""

    # Override session dependency in FastAPI with the test session
    main_app.dependency_overrides[sql_db_helper.session_dependency] = (
        test_sql_db.session_dependency
    )

    async with AsyncClient(
        app=main_app,
        base_url="http://testserver",
    ) as ac:
        ac.cookies = {}
        yield ac
        ac.cookies = {}

    # Clear dependency overrides after the test
    main_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def superuser_client(session: AsyncSession, client: AsyncClient) -> AsyncClient:

    register_payload = {
        "email": "somemail@mail.com",
        "password": "PASSWORD",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "USERNAME",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    stmt = (
        update(User)
        .where(User.email == register_payload["email"])
        .values(is_superuser=True)
    )
    await session.execute(stmt)
    await session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "somemail@mail.com", "password": "PASSWORD"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {access_token}"
    yield client


@pytest.fixture(scope="function")
async def products(session: AsyncSession):
    products_lst = [
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Potato pie",
                    "product_description": "Pie with tender potatoes",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Пиріжок з картоплею",
                    "product_description": "Пиріжок з ніжною картоплею",
                },
            ],
            "price": 20,
            "category": "Patties",
            "stock_quantity": 200,
            "image_src": "https://i.imgur.com/gcIZ0Es.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with chicken, cheese and mushrooms",
                    "product_description": "Cheburek with chicken, cheese and mushrooms",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із куркою, сиром та грибами",
                    "product_description": "Чебурек із куркою, сиром та грибами",
                },
            ],
            "price": 65,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Cheburek with meat and cheese",
                    "product_description": "Cheburek with meat and cheese",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Чебурек із м'ясом та сиром",
                    "product_description": "Чебурек із м'ясом та сиром",
                },
            ],
            "price": 60,
            "category": "Chebureks",
            "stock_quantity": 100,
            "image_src": "https://i.imgur.com/RKUO3jK.png",
        },
        {
            "translations": [
                {
                    "language_code": "en",
                    "product_name": "Sprite 0.5l",
                    "product_description": "Sprite refreshing drink 0.5l",
                },
                {
                    "language_code": "ukr",
                    "product_name": "Спрайт 0.5л",
                    "product_description": "Освіжаючий напій Спрайт 0.5л",
                },
            ],
            "price": 30,
            "category": "Beverages",
            "stock_quantity": 300,
            "image_src": "https://i.imgur.com/l7RFgRd.png",
        },
    ]
    product_bulk = ProductBulkCreate(
        products=[ProductCreate(**product_obj) for product_obj in products_lst]
    )
    await ProductsService.bulk_create_product(session=session, products_in=product_bulk)
    return await ProductsService.get_products(session=session)
