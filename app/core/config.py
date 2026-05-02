from __future__ import annotations

from functools import lru_cache

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NeuralShield Digital"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    domain: str = "neuralshielddigital.com"
    public_email: EmailStr = "neuralshielddigital@gmail.com"
    business_email: EmailStr = "contact@neuralshielddigital.com"
    support_phone: str = "+91 9998344439"

    host: str = "0.0.0.0"
    port: int = 8000
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "neuralshielddigital.com", "www.neuralshielddigital.com"]
    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/neuralshielddigital"
    postgres_db: str = "neuralshielddigital"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    secret_key: str = "change-me-in-production"
    csrf_secret_key: str = "change-me-csrf-in-production"
    session_cookie_name: str = "nsd_admin_session"
    session_max_age_seconds: int = 28800
    secure_cookies: bool = False

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "contact@neuralshielddigital.com"
    smtp_from_name: str = "NeuralShield Digital"
    smtp_use_tls: bool = True

    log_level: str = "INFO"
    log_json: bool = False

    admin_default_email: EmailStr = "contact@neuralshielddigital.com"
    admin_default_password: str = "ChangeMe123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    @field_validator("allowed_hosts", "cors_origins", mode="before")
    @classmethod
    def parse_csv_list(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
