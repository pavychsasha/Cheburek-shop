import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User

from app.core.schemas.user import UserCreate
from app.core.dependencies.authentication.user_manager import UserManager


class UserService:
    @classmethod
    async def create_user(
        cls,
        user_manager: UserManager,
        user_create: UserCreate,
    ) -> User:
        await user_manager.create(
            user_create=user_create,
            safe=False,
        )

    @classmethod
    async def get_users(cls, session: AsyncSession) -> User:
        stmt = select(User)
        users = await session.execute(stmt)
        return users.scalars().all()
