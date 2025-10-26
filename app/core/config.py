"""Application configuration."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY_PREFIX: str = "fc"
    API_KEY_HEADER_NAME: str = "X-API-Key"
    ADMIN_PROVISION_TOKEN: Optional[str] = None

    # LLM APIs
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

    # Signal Intelligence APIs
    SEARCHAPI_KEY: Optional[str] = None

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Fieldcraft"
    BLUEPRINT_USE_LLM: bool = True
    BLUEPRINT_LLM_PROVIDER: str = "claude"
    BLUEPRINT_LLM_MAX_TOKENS: int = 2800
    RATE_LIMIT_REQUESTS_PER_MINUTE: Optional[int] = None
    RATE_LIMIT_WINDOW_SECONDS: Optional[int] = 60
    RATE_LIMIT_REDIS_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
