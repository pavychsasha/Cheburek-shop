from fastapi_users.authentication import AuthenticationBackend
from app.api.dependencies.authentication.transport import (
    # bearer_transport,
    cookie_transport,
)
from app.api.dependencies.authentication.strategy import get_database_strategy


auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
