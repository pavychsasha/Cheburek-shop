import uuid
from sqlalchemy import Result, delete, select
from sqlalchemy.orm import joinedload

# import auth.utils as auth_utils
from core.models import User
from core.models import Order
from .schemas import UserCreate, UserUpdate, UserPartialUpdate


from sqlalchemy.ext.asyncio import AsyncSession


async def get_users(session: AsyncSession) -> list[User]:
    stmt = (
        select(User)
        .order_by(User.user_id)
        .options(
            joinedload(
                User.orders,
                Order.products,
            )
        )  # loading all of the stuff associated with user
    )
    result: Result = await session.execute(stmt)
    products = result.scalars().all()
    return list(products)


async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
    # validation stuff.... or pydantic level is fine? ...

    user = User(**user_create.model_dump())
    session.add(user)
    await session.commit()
    return user


async def get_user_by_user_id(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> User | None:
    # validation stuff.... or pydantic level is fine? ...

    stmt = select(User).where(User.user_id == user_id)
    user: User | None = await session.scalar(stmt)
    return user


async def update_user(
    session: AsyncSession,
    user: User,
    updated_user: UserUpdate | UserPartialUpdate,
    partial: bool = False,
) -> User:
    # validation stuff.... or pydantic level is fine? ...

    for name, value in updated_user.model_dump(exclude_unset=partial).items():
        setattr(user, name, value)
    await session.commit()
    return user


async def delete_user(session: AsyncSession, user_id: uuid.UUID) -> None:
    #  TODO: callers permissions checks...
    stmt = delete(User).where(User.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
