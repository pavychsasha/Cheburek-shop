import uuid

from core.models import User
from fastapi_users import FastAPIUsers
from api.dependencies.authentication.user_manager import get_user_manager
from api.dependencies.authentication.backend import auth_backend


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
