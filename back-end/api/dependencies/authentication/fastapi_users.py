import uuid

from core.models import User
from fastapi_users import FastAPIUsers
from api.dependencies.authentication import get_user_manager
from api.dependencies.authentication import auth_backend


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_super_user = fastapi_users.current_user(active=True, superuser=True)
