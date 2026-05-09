import asyncio
import contextlib
import os
from pathlib import Path

from fastapi_users.exceptions import UserAlreadyExists, UserNotExists

from app.core.schemas.user import UserCreate, UserUpdate
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


def load_local_env() -> None:
    for env_path in (Path(".env"), Path("back-end/.env")):
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            clean_line = line.strip()
            if (
                not clean_line
                or clean_line.startswith("#")
                or "=" not in clean_line
            ):
                continue
            key, value = clean_line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


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
    is_active: bool = default_is_active,
    is_superuser: bool = default_is_superuser,
    is_verified: bool = default_is_verified,
):
    async with sql_db_helper.session_factory() as session:
        async with get_users_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                try:
                    existing_user = await user_manager.get_by_email(email)
                    user_update = UserUpdate(
                        password=password,
                        is_active=is_active,
                        is_superuser=is_superuser,
                        is_verified=is_verified,
                    )
                    return await user_manager.update(
                        user_update=user_update,
                        user=existing_user,
                        safe=False,
                    )
                except UserNotExists:
                    user_create = UserCreate(
                        email=email,
                        password=password,
                        is_active=is_active,
                        is_superuser=is_superuser,
                        is_verified=is_verified,
                    )

                try:
                    user = await create_user(
                        user_manager=user_manager,
                        user_create=user_create,
                    )
                    return user
                except UserAlreadyExists:
                    existing_user = await user_manager.get_by_email(email)
                    return await user_manager.update(
                        user_update=UserUpdate(
                            password=password,
                            is_active=is_active,
                            is_superuser=is_superuser,
                            is_verified=is_verified,
                        ),
                        user=existing_user,
                        safe=False,
                    )


if __name__ == "__main__":
    load_local_env()
    email = os.getenv("ADMIN_EMAIL", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "").strip()
    if not email or email == "generated-by-setup":
        raise SystemExit("ADMIN_EMAIL is missing. Run ./setup.sh first.")
    if not password or password == "generated-by-setup":
        raise SystemExit("ADMIN_PASSWORD is missing. Run ./setup.sh first.")

    asyncio.run(create_superuser(email=email, password=password))
    print("Admin user is ready.")
