from app.core.config import settings
from fastapi_users.authentication import BearerTransport, CookieTransport

# TODO: update url
bearer_transport = BearerTransport(
    tokenUrl=settings.api.bearer_token_url,
)

cookie_transport = CookieTransport(
    cookie_httponly=settings.api.cookie_http_only,
    cookie_name="userauth",
)
