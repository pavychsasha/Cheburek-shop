from typing import Annotated

from fastapi import APIRouter, Depends, Security, Form, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin.services import AdminService
from app.core.dependencies.authentication.fastapi_users_dependency import (
    current_active_superuser,
)
from app.core.dependencies.authentication.user_manager import (
    get_user_manager,
    UserManager,
)
from app.core.schemas.admin import AdminCreate

router = APIRouter(tags=["Admin"], dependencies=[Security(current_active_superuser)])


@router.post("/", status_code=status.HTTP_200_OK)
async def create_admin(
    admin_create: Annotated[AdminCreate, Form()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    await AdminService.create_superuser(
        user_manager=user_manager, admin_user=admin_create
    )
