# app/config.py
from pydantic import MySQLDsn, field_validator, FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Application Metadata
    PROJECT_NAME: str = "IdeaHub MVP"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Anonymous idea submission and voting platform"

    # Environment Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Database Configuration (MySQL focused)
    DATABASE_URL: MySQLDsn = "mysql+aiomysql://user:pass@localhost:3306/ideahub_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    @field_validator("DATABASE_URL")
    def validate_db_url(cls, v: str, info: FieldValidationInfo):
        if "mysql" not in v:
            raise ValueError("Only MySQL/MariaDB is supported")

        if "@localhost" in v and info.data.get("ENVIRONMENT") == "production":
            logger.warning("Using default localhost database in production!")

        # Add SSL requirement for production
        if info.data.get("ENVIRONMENT") == "production" and "ssl_ca" not in v:
            raise ValueError("Production database requires SSL configuration")

        return v

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-please-change-in-prod")
    RECAPTCHA_SECRET: str = os.getenv("RECAPTCHA_SECRET", "")

    # Rate Limiting
    SUBMISSION_RATE_LIMIT: str = os.getenv("SUBMISSION_RATE_LIMIT", "5/minute")
    VOTING_RATE_LIMIT: str = os.getenv("VOTING_RATE_LIMIT", "1/second")

    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000")

    @property
    def cors_origins(self):
        return self.ALLOWED_ORIGINS.split(",")

    # Monitoring
    PROMETHEUS_DIR: str = "/tmp/metrics"
    ENABLE_PROMETHEUS: bool = True

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        case_sensitive=True,
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    logger.info(f"Loaded settings for {settings.ENVIRONMENT} environment")
    return settings


settings = get_settings()
