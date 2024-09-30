from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, Indexed, init_beanie

from app.core.config import settings
from app.core.models.cart import all_document_models


class SQLDatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session
            await session.close()


class MongoDbHelper:
    def __init__(self, db_url: str, db_name: str):
        self.db_url: str = db_url
        self.db_name: str = db_name
        self.client: Optional[AsyncIOMotorClient] = None

    async def connect(self):
        """Starts the MongoDB client and connects to the database."""
        self.client = AsyncIOMotorClient(
            self.db_url,
            uuidRepresentation="standard",
        )
        await init_beanie(
            database=self.client.db_name, document_models=all_document_models  # type: ignore
        )
        print("MongoDB connected.")


sql_db_helper = SQLDatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)

mongo_db_helper = MongoDbHelper(
    db_url=settings.mongo_db.url,
    db_name=settings.mongo_db.database_name,
)
