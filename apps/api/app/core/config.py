import json
from functools import lru_cache
from typing import Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CareerOS"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/careeros"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/careeros"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI
    OPENAI_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    # Job Search APIs
    ADZUNA_APP_ID: str = ""
    ADZUNA_APP_KEY: str = ""
    JOOBLE_API_KEY: str = ""
    RAPIDAPI_KEY: str = ""

    # Storage
    S3_BUCKET: str = ""
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    CORS_ORIGIN_REGEX: str = r"^https://.*\.vercel\.app$"
    FRONTEND_URL: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        origins: list[str] = []
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        origins = [str(i).strip().rstrip("/") for i in parsed if str(i).strip()]
                except Exception:
                    pass
            if not origins:
                origins = [i.strip().strip("'\"").rstrip("/") for i in v_str.split(",") if i.strip()]
        elif isinstance(v, list):
            origins = [str(i).strip().rstrip("/") for i in v if str(i).strip()]

        if not origins:
            origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
        return list(dict.fromkeys(origins))

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env", "apps/api/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
