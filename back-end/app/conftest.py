# conftest.py

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.main import app as main_app
from app.core.models import SQLDatabaseHelper, sql_db_helper
from app.core.models import Base

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

    yield  # Control passes to the test function


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("reset_databases")
async def client(test_sql_db):
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
