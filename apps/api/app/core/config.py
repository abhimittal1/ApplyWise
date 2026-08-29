import json
import logging
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CareerOS"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "careeros-api"
    JWT_AUDIENCE: str = "careeros-app"
    RSA_PRIVATE_KEY: str = ""
    RSA_PUBLIC_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/careeros"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/careeros"

    # Redis & Task Queue Infrastructure
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SSL_VERIFY: bool = True
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_SOCKET_TIMEOUT: float = 2.0
    REDIS_CONNECT_TIMEOUT: float = 2.0
    REDIS_DEFAULT_CACHE_TTL: int = 3600  # Default 1 hour TTL
    REDIS_MAX_CACHE_TTL: int = 86400  # Maximum 24 hour TTL guardrail

    # Network Security / Reverse Proxy
    TRUSTED_PROXIES: list[str] = ["127.0.0.1", "::1"]

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
    S3_ENDPOINT_URL: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    CORS_ORIGIN_REGEX: str = ""
    FRONTEND_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str | None) -> str:
        if not v:
            return "postgresql+asyncpg://postgres:postgres@localhost:5432/careeros"
        url = str(v).strip()
        # Convert postgres:// or postgresql:// to postgresql+asyncpg://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Convert sslmode query parameter for asyncpg compatibility
        if "sslmode=" in url:
            url = (
                url.replace("sslmode=require", "ssl=require")
                .replace("sslmode=prefer", "ssl=prefer")
                .replace("sslmode=disable", "ssl=disable")
                .replace("sslmode=verify-ca", "ssl=verify-ca")
                .replace("sslmode=verify-full", "ssl=verify-full")
            )
        return url

    @field_validator("DATABASE_URL_SYNC", mode="before")
    @classmethod
    def assemble_database_url_sync(cls, v: str | None) -> str:
        if not v:
            return ""
        url = str(v).strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        elif url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url

    @field_validator("TRUSTED_PROXIES", mode="before")
    @classmethod
    def assemble_trusted_proxies(cls, v: str | list[str]) -> list[str]:
        proxies: list[str] = []
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        proxies = [str(i).strip() for i in parsed if str(i).strip()]
                except Exception:
                    pass
            if not proxies:
                proxies = [i.strip().strip("'\"") for i in v_str.split(",") if i.strip()]
        elif isinstance(v, list):
            proxies = [str(i).strip() for i in v if str(i).strip()]

        if not proxies:
            proxies = ["127.0.0.1", "::1"]
        return list(dict.fromkeys(proxies))

    @model_validator(mode="after")
    def sync_database_urls(self) -> "Settings":
        # Derive DATABASE_URL_SYNC from DATABASE_URL if not explicitly set or if default localhost while DATABASE_URL is remote
        is_sync_default = not self.DATABASE_URL_SYNC or (
            "localhost" in self.DATABASE_URL_SYNC and "localhost" not in self.DATABASE_URL
        )
        if is_sync_default:
            sync_url = self.DATABASE_URL
            if sync_url.startswith("postgresql+asyncpg://"):
                sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            elif sync_url.startswith("postgres://"):
                sync_url = sync_url.replace("postgres://", "postgresql://", 1)
            if "ssl=require" in sync_url and "sslmode=" not in sync_url:
                sync_url = sync_url.replace("ssl=require", "sslmode=require")
            self.DATABASE_URL_SYNC = sync_url
        elif self.DATABASE_URL_SYNC.startswith("postgres://"):
            self.DATABASE_URL_SYNC = self.DATABASE_URL_SYNC.replace("postgres://", "postgresql://", 1)
        elif self.DATABASE_URL_SYNC.startswith("postgresql+asyncpg://"):
            self.DATABASE_URL_SYNC = self.DATABASE_URL_SYNC.replace("postgresql+asyncpg://", "postgresql://", 1)
        return self

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() in ("production", "prod"):
            if self.SECRET_KEY in ("change-me-in-production", "secret", "default", "") or len(self.SECRET_KEY) < 16:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: A secure, random SECRET_KEY (min 16 chars) must be provided in production!"
                )
            if self.REDIS_URL.startswith("redis://") and not any(h in self.REDIS_URL for h in ("localhost", "127.0.0.1")):
                logger.warning(
                    "SECURITY WARNING: Production REDIS_URL is using unencrypted redis:// instead of rediss:// (TLS)."
                )
            if "@" not in self.REDIS_URL:
                logger.warning(
                    "SECURITY WARNING: Production REDIS_URL does not contain authentication credentials."
                )
        return self

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
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
