"""Central, typed configuration. All values can be overridden with SMS_* env vars."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT_KEY = "change-me-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SMS_", extra="ignore")

    app_name: str = "Student Management System"
    api_prefix: str = "/api/v1"
    environment: Literal["dev", "test", "prod"] = "dev"

    database_url: str = "sqlite:///./data/sms.db"
    db_echo: bool = False

    secret_key: SecretStr = SecretStr(_INSECURE_DEFAULT_KEY)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: list[str] = []
    log_level: str = "INFO"
    log_json: bool = False

    @model_validator(mode="after")
    def _forbid_insecure_prod(self) -> "Settings":
        if self.environment == "prod" and self.secret_key.get_secret_value() == _INSECURE_DEFAULT_KEY:
            raise ValueError("SMS_SECRET_KEY must be set to a strong secret in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
