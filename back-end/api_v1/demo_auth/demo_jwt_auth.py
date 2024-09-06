from api_v1.demo_auth.validation import (
    get_current_active_auth_user,
    get_current_token_payload,
    get_current_auth_user_for_refresh,
    validate_auth_user,
)
from pydantic import BaseModel

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import (
    # HTTPAuthorizationCredentials,
    HTTPBearer,
)

from users.schemas import UserSchema
from api_v1.demo_auth.helpers import (
    create_access_token,
    create_refresh_token,
)


http_bearer = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(
    tags=["JWT"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/login/")
def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user),
):

    token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh/",
    response_model=TokenInfo,
    response_model_exclude=None,
)
def auth_refresh_jwt(
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
):

    access_token = create_access_token(user)

    return TokenInfo(
        access_token=access_token,
    )


@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user),
):

    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": payload.get(
            "iat",
        ),
    }
