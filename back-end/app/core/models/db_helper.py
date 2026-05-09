from typing import AsyncGenerator, Optional


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from redis.asyncio import Redis


from app.core.config import settings
from app.core.models.cart import all_document_models
from app.core.caching.cache import RedisCache


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
                database=self.client[self.db_name], document_models=all_document_models  # type: ignore
            )
            print(f"MongoDB connected to {self.db_name}.")
        except Exception as e:
            print(f"Error initializing MongoDB: {e}")

    async def dispose(self):
        """Closes the MongoDB client."""
        if self.client:
            self.client.close()
            print(f"MongoDB connection to {self.db_name} closed.")


class RedisDbHelper:
    def __init__(self, host: str, port: int, db: int):
        self.redis: Optional[Redis] = None
        self.host = host
        self.port = port
        self.db = db
        self.cache: Optional[RedisCache] = None

    async def connect(self):
        """Connects to the Redis instance and initializes the RedisCache."""
        self.redis = Redis(host=self.host, port=self.port, db=self.db)
        self.cache = RedisCache(self.redis)
        print(f"Connected to Redis at {self.host}:{self.port}, DB {self.db}.")

    async def dispose(self):
        """Closes the Redis connection."""
        if self.redis:
            await self.redis.aclose()
            print("Redis connection closed.")


sql_db_helper = SQLDatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)

mongo_db_helper = MongoDbHelper(
    db_url=settings.mongo_db.connection_url,
    db_name=settings.mongo_db.database_name,
)

redis_db_helper = RedisDbHelper(
    host=settings.redis.host,
    port=settings.redis.port,
    db=settings.redis.db,
)
