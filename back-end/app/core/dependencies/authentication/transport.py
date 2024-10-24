from app.core.config import settings
from fastapi_users.authentication import BearerTransport, CookieTransport

# TODO: update url
bearer_transport = BearerTransport(
    tokenUrl=settings.api.bearer_token_url,
)


cookie_transport = CookieTransport(
    cookie_httponly=settings.cookie_transport_settings.cookie_http_only,
    cookie_name=settings.cookie_transport_settings.cookie_name,
    cookie_samesite=settings.cookie_transport_settings.cookie_samesite,
    cookie_secure=settings.cookie_transport_settings.cookie_secure,
)
