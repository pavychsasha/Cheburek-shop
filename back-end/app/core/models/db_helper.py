from asyncio import current_task
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


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
        self.db_url = db_url
        self.db_name = db_name
        self.client = None
        self.db = None

    async def connect(self):
        """Starts the MongoDB client and connects to the database."""
        self.client = AsyncIOMotorClient(
            self.db_url,
            uuidRepresentation="standard",
        )
        self.db = self.client[self.db_name]
        print("MongoDB connected.")

    async def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            await self.client.close()  # type: ignore
            print("MongoDB connection closed.")

    async def mongo_session_dependency(self):
        """Dependency that provides a MongoDB connection session."""
        if self.db is None:  # type: ignore
            await self.connect()
        try:
            yield self.db
        finally:
            pass


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
