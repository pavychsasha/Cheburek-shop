# tests/conftest.py
import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.models.base import Base
from core.models import User, Product, Order, Reward

DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def async_session(async_engine):
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session


@pytest.fixture(scope="session")
async def db_session(async_session):
    async with async_session() as session:
        yield session


@pytest.fixture(scope="session")
async def user_fixture(async_session):
    async with async_session() as session:
        user = User(
            user_id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password="hashedpassword",
            reward_points=100,
        )
        session.add(user)
        await session.commit()
        return user


@pytest.fixture(scope="session")
async def product_fixture(async_session):
    async with async_session() as session:
        product = Product(
            product_id=uuid.uuid4(),
            name="Test Product",
            description="A test product",
            price=10.0,
            category="Test Category",
            stock_quantity=50,
            points=10,
        )
        session.add(product)
        await session.commit()
        return product


@pytest.fixture(scope="session")
async def order_fixture(async_session, user_fixture):
    async with async_session() as session:
        order = Order(
            order_id=uuid.uuid4(),
            user_id=user_fixture.user_id,
            status="pending",
            payment_method="card",
        )
        session.add(order)
        await session.commit()
        return order


@pytest.fixture(scope="session")
async def reward_fixture(async_session):
    async with async_session() as session:
        reward = Reward(
            reward_id=uuid.uuid4(),
            name="Test Reward",
            description="A test reward",
            points_required=50,
        )
        session.add(reward)
        await session.commit()
        return reward


# @pytest.fixture
# async def db_session(db_session):
#     async with db_session.begin():
#         yield db_session
#     await db_session.rollback()
