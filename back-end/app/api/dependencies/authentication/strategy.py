from __future__ import annotations

from typing import Annotated

from app.api.dependencies.authentication.access_tokens import \
    get_access_tokens_db
from app.core.config import settings
from app.core.models import AccessToken
from fastapi import Depends
from fastapi_users.authentication.strategy.db import (AccessTokenDatabase,
                                                      DatabaseStrategy)


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken],
        Depends(get_access_tokens_db),
    ]
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )
