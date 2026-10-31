"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the YouTube AI Automation Agent."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "YouTube AI Automation Agent"
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    youtube_client_secret: str = Field(default="client_secret.json", alias="YOUTUBE_CLIENT_SECRET")
    youtube_client_id: str = Field(default="", alias="YOUTUBE_CLIENT_ID")
    youtube_token_file: str = "token.json"

    database_url: str = Field(default="sqlite:///database/youtube_agent.db", alias="DATABASE_URL")

    ollama_url: str = Field(default="http://localhost:11434", alias="OLLAMA_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")

    upload_interval: int = Field(default=30, alias="UPLOAD_INTERVAL")
    upload_folder: str = Field(default="videos", alias="UPLOAD_FOLDER")
    uploaded_folder: str = Field(default="uploaded", alias="UPLOADED_FOLDER")
    failed_folder: str = Field(default="failed", alias="FAILED_FOLDER")
    thumbnail_folder: str = Field(default="thumbnails", alias="THUMBNAILS_FOLDER")
    generated_folder: str = Field(default="generated", alias="GENERATED_FOLDER")

    youtube_default_visibility: str = "private"
    youtube_default_language: str = "en"
    youtube_default_category_id: str = "22"

    retry_attempts: int = 3

    def ensure_directories(self, project_root: Path) -> None:
        """Create required runtime directories when missing."""

        for directory in [
            self.upload_folder,
            self.uploaded_folder,
            self.failed_folder,
            self.thumbnail_folder,
            self.generated_folder,
            "database",
            "app/logs",
        ]:
            (project_root / directory).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
