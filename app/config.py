from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "API Integration Hub"
    database_url: str = "sqlite:///./data/appointments.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# make sure sqlite folder exists when using the default path
if settings.database_url.startswith("sqlite:///./"):
    Path("data").mkdir(exist_ok=True)
