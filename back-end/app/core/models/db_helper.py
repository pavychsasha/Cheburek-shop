from typing import AsyncGenerator, Optional

from app.core.config import settings
from app.core.models.cart import all_document_models
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)


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
        """Dispose the SQL engine."""
        try:
            await self.engine.dispose()
        except SQLAlchemyError as e:
            print(f"Error disposing SQL engine: {e}")

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """Generate sessions for dependency injection in FastAPI."""
        async with self.session_factory() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                print(f"Session rollback due to error: {e}")
                raise  # Re-raise the exception to avoid hiding errors
            finally:
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
        try:
            # Initialize Beanie with the correct database
            await init_beanie(
                # type: ignore
                database=self.client[self.db_name], document_models=all_document_models
            )
            print(f"MongoDB connected to {self.db_name}.")
        except Exception as e:
            print(f"Error initializing MongoDB: {e}")

    async def dispose(self):
        """Closes the MongoDB client."""
        if self.client:
            self.client.close()
            print(f"MongoDB connection to {self.db_name} closed.")


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
