from __future__ import annotations

import uuid
import logging
from typing import TYPE_CHECKING, Optional

from app.core.dependencies.authentication.users import get_users_db
from app.core.config import settings
from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin

from app.core.models import User


if TYPE_CHECKING:
    from fastapi import Request


log = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        log.warning(
            "User %r has registered.",
            user.id,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        log.warning(
            "Password reset requested for user %r.",
            user.id,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        log.warning(
            "Verification requested for user %r.",
            user.id,
        )


async def get_user_manager(user_db=Depends(get_users_db)):
    yield UserManager(user_db)
