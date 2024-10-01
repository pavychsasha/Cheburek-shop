from typing import Optional, Annotated
import uuid

from app.core.models import User
from fastapi import Depends
from fastapi_users import FastAPIUsers
from app.api.dependencies.authentication.user_manager import get_user_manager
from app.api.dependencies.authentication.backend import auth_backend


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
current_user = fastapi_users.current_user(optional=True)


async def current_user_id(
    current_user: Annotated[Optional[User], Depends(current_user)],
) -> Optional[uuid.UUID]:
    if current_user:
        return current_user.id
