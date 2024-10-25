from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.users.services import UserService
from app.core.schemas.admin import AdminCreate

from app.core.schemas.user import UserCreate
from app.core.dependencies.authentication.user_manager import UserManager


class AdminService:
    @classmethod
    async def create_superuser(
        cls,
        admin_user: AdminCreate,
        user_manager: UserManager,
    ):
        user_create = UserCreate(
            email=admin_user.email,
            password=admin_user.password,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        await UserService.create_user(
            user_manager=user_manager,
            user_create=user_create,
        )
