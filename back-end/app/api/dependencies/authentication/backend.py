from app.api.dependencies.authentication.strategy import get_database_strategy
from app.api.dependencies.authentication.transport import cookie_transport
from fastapi_users.authentication import AuthenticationBackend

auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
