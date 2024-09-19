from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Optional

from api.dependencies.authentication.users import get_users_db
from core.config import settings
from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin


if TYPE_CHECKING:
    import uuid
    from fastapi import Request
    from core.models.user import User


log = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        log.info(
            "User %r has registered.",
            user.id,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        log.info(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        log.info(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )


async def get_user_manager(user_db=Depends(get_users_db)):
    yield UserManager(user_db)
