from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    debug: bool = False
    app_port: int = 8000
    app_name: str = "Events Aggregator"

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_database: str = ""
    postgres_username: str = ""
    postgres_password: str = ""

    db_echo: bool = False
    db_pool_pre_ping: bool = True

    events_provider_base_url: str = ""
    events_provider_api_key: SecretStr = SecretStr("")



    @property
    def db_url(self) -> URL:
        return URL.create(
            "postgresql+asyncpg",
            self.postgres_username,
            self.postgres_password,
            self.postgres_host,
            self.postgres_port,
            self.postgres_database,
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
