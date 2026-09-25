import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerLens AI"
    API_V1_PREFIX: str = "/api/v1"
    APP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"

    # SerpApi (Optional: for real-time live Google Jobs search fallback)
    SERPAPI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///data/sessions.db"

    # Directory Paths
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent)
    APP_DIR: str = str(Path(__file__).resolve().parent.parent)
    DATA_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "data")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
