from core.schemas.user import UserCreate, UserRead
from fastapi import APIRouter
from api.dependencies.authentication.fastapi_users import fastapi_users
from api.dependencies.authentication import auth_backend

router = APIRouter(
    tags=["Auth"],
)

# /login
# /logout
router.include_router(
    router=fastapi_users.get_auth_router(
        backend=auth_backend,
    ),
)


# /register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)


# /request-verify-token
# /verify
router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)


router.include_router(
    router=fastapi_users.get_reset_password_router(),
)
