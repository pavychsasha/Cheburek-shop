import asyncio
import contextlib

from fastapi_users.exceptions import UserAlreadyExists

from app.core.schemas.user import UserCreate
from app.core.dependencies.authentication.user_manager import (
    UserManager,
    get_user_manager,
)
from app.core.dependencies.authentication.users import get_users_db
from app.core.models import sql_db_helper, User


get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

default_is_active = True
default_is_superuser = True
default_is_verified = True


async def create_user(
    user_manager: UserManager,
    user_create: UserCreate,
) -> User:
    user = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(
    email: str,
    password: str,
    username: str,
    is_active: bool = default_is_active,
    is_superuser: bool = default_is_superuser,
    is_verified: bool = default_is_verified,
):
    user_create = UserCreate(
        email=email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
        username=username,
    )

    async with sql_db_helper.session_factory() as session:
        async with get_users_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                try:
                    user = await create_user(
                        user_manager=user_manager,
                        user_create=user_create,
                    )
                    print(f"User created {user}")
                    return user
                except UserAlreadyExists:
                    print(f"User already exists {user_create}")


if __name__ == "__main__":
    email = str(input("Enter admin-user's email (admin@mail.com): "))
    if not email:
        email = "admin@mail.com"
    password = str(input("Enter admin-user's password (adminpassword): "))
    if not password:
        password = "adminpassword"
    username = str(input("Enter admin-user's username (adminusername): "))
    if not username:
        username = "adminusername"
    asyncio.run(create_superuser(email=email, password=password, username=username))
