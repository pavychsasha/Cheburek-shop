from core.config import settings
from fastapi_users.authentication import BearerTransport

# TODO: update url
bearer_transport = BearerTransport(
    tokenUrl=settings.api.bearer_token_url,
)
