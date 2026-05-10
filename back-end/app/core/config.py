from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8091


class CorsConfig(BaseModel):
    allowed_origins: str = (
        "http://app.local.cheburek-shop.com,"
        "http://admin.local.cheburek-shop.com,"
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
    settings: str = "/settings"
    analytics: str = "/analytics"


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


class MediaConfig(BaseModel):
    endpoint: str = "minio:9000"
    access_key: str
    secret_key: str
    bucket: str = "cheburek-product-images"
    public_base_url: str = "http://api.local.cheburek-shop.com/media"
    secure: bool = False
    max_image_upload_mb: int = 5

    @property
    def max_image_upload_bytes(self) -> int:
        return self.max_image_upload_mb * 1024 * 1024


class CurrencyConfig(BaseModel):
    base_currency: str = "UAH"
    default_currency: str = "UAH"
    supported_currencies: str = "UAH,USD,EUR"
    currency_rates: str = "UAH:1,USD:0.024,EUR:0.022"
    currency_symbols: str = "UAH:\u20b4,USD:$,EUR:\u20ac"

    @property
    def supported_currency_codes(self) -> list[str]:
        return [
            currency.strip().upper()
            for currency in self.supported_currencies.split(",")
            if currency.strip()
        ]

    @staticmethod
    def _parse_mapping(raw_value: str, value_type=str) -> dict[str, str | float]:
        mapping: dict[str, str | float] = {}
        for pair in raw_value.split(","):
            if ":" not in pair:
                continue
            key, value = pair.split(":", 1)
            normalized_key = key.strip().upper()
            if normalized_key:
                mapping[normalized_key] = value_type(value.strip())
        return mapping

    @property
    def rate_mapping(self) -> dict[str, float]:
        return {
            currency: float(rate)
            for currency, rate in self._parse_mapping(
                self.currency_rates, float
            ).items()
        }

    @property
    def symbol_mapping(self) -> dict[str, str]:
        return {
            currency: str(symbol)
            for currency, symbol in self._parse_mapping(
                self.currency_symbols, str
            ).items()
        }


class ProductLanguageConfig(BaseModel):
    supported_languages: str = "en,ukr"
    auto_translate_products: bool = True

    @property
    def language_codes(self) -> list[str]:
        normalized = [
            language.strip().lower()
            for language in self.supported_languages.split(",")
            if language.strip()
        ]
        return list(dict.fromkeys(normalized)) or ["en", "ukr"]


class TranslationConfig(BaseModel):
    enabled: bool = False
    base_url: str = "http://translator:5000"
    timeout_seconds: float = Field(default=3.0, gt=0)
    source_language: str = "en"


class AccessToken(BaseModel):
    lifetime_seconds: int = Field(default=60 * 60 * 24 * 30, ge=300)
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
    media: MediaConfig
    currency: CurrencyConfig = CurrencyConfig()
    product_languages: ProductLanguageConfig = ProductLanguageConfig()
    translation: TranslationConfig = TranslationConfig()
    session: Session


settings = Settings()  # type: ignore
