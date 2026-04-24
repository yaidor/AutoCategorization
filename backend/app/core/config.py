from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SALESCAT_",
        case_sensitive=False,
        extra="ignore",
    )

    environment: str = "development"


settings = Settings()
