from fastapi_users.authentication import AuthenticationBackend
from core.authentication.transport import bearer_transport
from api.dependencies.strategy import get_database_strategy


auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
