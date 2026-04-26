from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _read_version() -> str:
    try:
        return pkg_version("salescat-api")
    except PackageNotFoundError:
        return "0.0.0"


VERSION = _read_version()


def _parse_csv(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SALESCAT_",
        case_sensitive=False,
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://salescat:salescat@localhost:5432/salescat"
    redis_url: str = "redis://localhost:6379/0"

    cors_origins: Annotated[list[str], NoDecode, BeforeValidator(_parse_csv)] = [
        "http://localhost:5173"
    ]

    llm_provider: str = "mock"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_timeout_seconds: float = 30.0
    llm_max_concurrent: int = 5


settings = Settings()
