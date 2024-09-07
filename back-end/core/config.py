import os
from pathlib import Path
from core.models import access_token
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent.parent

class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    messages: str = "/messages"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # api/v1/auth/login
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        # return path[1:]
        return path.removeprefix("/")

class DbSettings(BaseModel):
    url: str = f"postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:5432/{os.getenv("POSTGRES_DB")}"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


# class AuthJWT(BaseModel):
#     private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
#     public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
#     algorithm: str = "RS256"
#     access_token_expire_minutes: int = 15
#     refresh_token_expire_days: int = 30

class AccessToken(BaseModel):
    lifetime_seconds: int = 3600



class Settings(BaseSettings):
    api: ApiPrefix = ApiPrefix()
    db: DbSettings = DbSettings()
    access_token: AccessToken = AccessToken()


settings = Settings()
