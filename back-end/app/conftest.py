# conftest.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.main import app as main_app
from app.core.models import SQLDatabaseHelper, sql_db_helper
from app.core.models import Base
from app.core.models.cart import all_document_models  # Your Beanie document models
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Override settings to use test databases
settings.db.url = settings.db.test_url
settings.mongo_db.url = settings.mongo_db.test_url
settings.mongo_db.database_name = settings.mongo_db.test_database_name

# Create a test SQLDatabaseHelper instance


@pytest.fixture(scope="function")
async def test_sql_db():
    test_sql_db_helper = SQLDatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )
    return test_sql_db_helper


@pytest.fixture(scope="function", autouse=True)
async def reset_databases(test_sql_db):
    """Fixture to drop and recreate all databases before each test."""
    # Drop and recreate SQL database tables
    async with test_sql_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Drop all collections in MongoDB
    # client = AsyncIOMotorClient(
    #     settings.mongo_db.test_url, uuidRepresentation="standard"
    # )
    # db = client[settings.mongo_db.database_name]
    # collections = await db.list_collection_names()
    # for collection in collections:
    #     await db.drop_collection(collection)
    # client.close()

    # # Initialize Beanie with the test MongoDB
    # await init_beanie(
    #     database=client[settings.mongo_db.database_name],
    #     document_models=all_document_models,
    # )

    yield  # Control passes to the test function

    # No need to clean up after the test, as we're resetting before each test


@pytest.fixture(scope="function")
async def client(reset_databases, test_sql_db):
    """Set up a FastAPI client for testing."""

    # Replace 'sql_db_helper.session_dependency' with your actual dependency function
    main_app.dependency_overrides[sql_db_helper.session_dependency] = (
        test_sql_db.session_dependency
    )

    # Use AsyncClient for making HTTP requests in tests
    async with AsyncClient(app=main_app, base_url="http://testserver") as ac:
        yield ac

    # Clear dependency overrides after the test
    main_app.dependency_overrides = {}
