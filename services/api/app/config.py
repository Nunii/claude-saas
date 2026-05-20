"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app config. Reads from env vars; falls back to defaults below."""

    # Service
    app_name: str = "claude-saas-api"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://claude:claude@localhost:5432/claude_saas"

    # Anthropic
    anthropic_api_key: str = ""  # Set in env, required for /v1/chat to work
    anthropic_model: str = "claude-sonnet-4-5"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
