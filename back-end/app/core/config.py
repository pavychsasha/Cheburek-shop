from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8091


class CorsConfig(BaseModel):
    allowed_origins: str = (
        "http://app.local.cheburek-shop.com:5178,"
        "http://admin.local.cheburek-shop.com:5178,"
        "http://localhost:5178,"
        "http://127.0.0.1:5178"
    )

    @property
    def origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    products: str = "/products"
    cart: str = "/cart"
    orders: str = "/orders"
    admin: str = "/admin"
    languages: str = "/languages"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # v1/v1/auth/login
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)

        return path.removeprefix("/")


class DatabaseConfig(BaseModel):
    # url: PostgresDsn
    url: str
    test_url: str
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


class MongoDatabaseCollections(BaseModel):
    carts: str = "carts"


class MongoDatabaseConfig(BaseModel):
    # username: str
    # password: str

    host: str = "mongo"
    port: int = 27017
    database_name: str = "cheburek_mongo_db"
    test_database_name: str = "test_cheburek_mongo_db"
    url: str | None = None
    collections: MongoDatabaseCollections = MongoDatabaseCollections()

    @property
    def connection_url(self) -> str:
        return self.url or f"mongodb://{self.host}:{self.port}/{self.database_name}"

    @property
    def test_url(self) -> str:
        # username = quote_plus(self.username)
        # password = quote_plus(self.password)
        mongo_db_uri = f"mongodb://{self.host}:{self.port}/{self.test_database_name}"
        return mongo_db_uri


class RedisDatabaseConfig(BaseModel):
    host: str = "redis"
    port: int = 6379
    db: int = 0


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class Session(BaseModel):
    secret_key: str


class CookieTransportSettings(BaseModel):
    cookie_http_only: bool = True
    cookie_name: str = "userauth"
    cookie_samesite: str = "lax"
    cookie_secure: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    cors: CorsConfig = CorsConfig()
    api: ApiPrefix = ApiPrefix()
    cookie_transport_settings: CookieTransportSettings = CookieTransportSettings()
    db: DatabaseConfig
    access_token: AccessToken
    mongo_db: MongoDatabaseConfig = MongoDatabaseConfig()
    redis: RedisDatabaseConfig = RedisDatabaseConfig()
    session: Session


settings = Settings()  # type: ignore
