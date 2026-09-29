from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerLens AI"
    API_V1_PREFIX: str = "/api/v1"
    APP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"

    # TypeSafe Jev API Key
    TYPESAFE_API_KEY: str = ""

    # Groq & LLM Config
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # LangSmith Observability Config
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "careerlens-resume-screener"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # Hugging Face Token (for ConvAI Laya & model hub access)
    HF_TOKEN: str = ""

    # Database
    DATABASE_URL: str = ""

    # Operational constraints
    MAX_UPLOAD_SIZE_MB: int = 5
    MAX_BATCH_SIZE: int = 15
    MAX_CONCURRENT_EVALUATIONS: int = 3

    # Directory Paths
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent)
    APP_DIR: str = str(Path(__file__).resolve().parent.parent)
    DATA_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "data")

    @property
    def resolved_database_url(self) -> str:
        """Returns the configured database URL or defaults to the sqlite path in DATA_DIR."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        data_path = Path(self.DATA_DIR)
        data_path.mkdir(parents=True, exist_ok=True)
        db_file = data_path / "sessions.db"
        return f"sqlite:///{db_file}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Synchronize LangSmith & Groq environment variables for LangChain SDK auto-discovery
import os

if settings.GROQ_API_KEY and not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

if settings.LANGCHAIN_TRACING_V2.lower() in ("true", "1") or os.environ.get("LANGCHAIN_TRACING_V2", "").lower() in ("true", "1"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    if settings.LANGCHAIN_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
    if settings.LANGCHAIN_ENDPOINT:
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT

