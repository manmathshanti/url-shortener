from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "URL Shortener"
    debug: bool = False
    base_url: str = "http://localhost:8000"

    # Mode switch
    test_mode: bool = True

    # Local database
    db_engine: str = "postgres"
    db_name: str = "url_shortener"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_sslmode: str = "disable"

    # Aiven database
    aiven_db_engine: str = "postgres"
    aiven_db_name: str = "defaultdb"
    aiven_db_host: str = "localhost"
    aiven_db_port: int = 5432
    aiven_db_user: str = "avnadmin"
    aiven_db_password: str = ""
    aiven_db_sslmode: str = "require"

    @computed_field
    @property
    def active_db_host(self) -> str:
        return self.db_host if self.test_mode else self.aiven_db_host

    @computed_field
    @property
    def active_db_port(self) -> int:
        return self.db_port if self.test_mode else self.aiven_db_port

    @computed_field
    @property
    def active_db_user(self) -> str:
        return self.db_user if self.test_mode else self.aiven_db_user

    @computed_field
    @property
    def active_db_password(self) -> str:
        return self.db_password if self.test_mode else self.aiven_db_password

    @computed_field
    @property
    def active_db_name(self) -> str:
        return self.db_name if self.test_mode else self.aiven_db_name

    @computed_field
    @property
    def active_db_sslmode(self) -> str:
        return self.db_sslmode if self.test_mode else self.aiven_db_sslmode

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.active_db_user}:{self.active_db_password}"
            f"@{self.active_db_host}:{self.active_db_port}/{self.active_db_name}"
        )

    @computed_field
    @property
    def db_ssl_required(self) -> bool:
        return self.active_db_sslmode in ("require", "verify-ca", "verify-full")

    # JWT
    secret_key: str = "change-this-to-a-long-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 3600

    # PostgreSQL schema — keeps our tables isolated from other apps on the same DB
    db_schema: str = "url_shortener"

    # URL
    short_code_length: int = 7
    rate_limit_per_minute: int = 60

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
