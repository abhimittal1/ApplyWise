import json
import logging
from typing import Any, Type, TypeVar
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.rate_limit import get_redis_client

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar("T", bound=BaseModel)


class CacheService:
    """
    Secure Redis Caching Service.
    Enforces:
    1. Strict tenant and environment namespacing (applywise:{env}:{namespace}:{tenant_id}:{resource_id})
    2. Pure JSON serialization / deserialization (strictly no pickle/eval/binary execution)
    3. Mandatory TTLs to prevent memory exhaustion DoS attacks
    4. Graceful fallthrough on cache errors
    """

    @staticmethod
    def format_key(namespace: str, tenant_id: str, resource_id: str) -> str:
        """
        Build a secure, strictly namespaced Redis key.
        Prevents cross-account cache poisoning and collisions across environments.
        """
        env = settings.ENVIRONMENT.lower().strip()
        clean_ns = namespace.strip(": ")
        clean_tenant = str(tenant_id).strip(": ")
        clean_resource = str(resource_id).strip(": ")
        return f"applywise:{env}:{clean_ns}:{clean_tenant}:{clean_resource}"

    @classmethod
    async def get(cls, key: str) -> Any | None:
        """Retrieve and JSON-deserialize a value from Redis."""
        client = get_redis_client()
        if client is None:
            return None
        try:
            raw = await client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}")
            return None

    @classmethod
    async def get_model(cls, key: str, model_class: Type[T]) -> T | None:
        """Retrieve and parse a Pydantic model from Redis cache."""
        data = await cls.get(key)
        if data is None:
            return None
        try:
            if isinstance(data, dict):
                return model_class.model_validate(data)
            return None
        except Exception as e:
            logger.warning(f"Failed to validate cached model for key '{key}': {e}")
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """
        Set a value in Redis with mandatory TTL.
        Enforces maximum TTL boundary to prevent unbounded memory growth.
        """
        client = get_redis_client()
        if client is None:
            return False

        # Enforce explicit TTL guardrails
        ttl = ttl_seconds if ttl_seconds is not None else settings.REDIS_DEFAULT_CACHE_TTL
        if ttl <= 0:
            raise ValueError("TTL must be a positive integer in seconds")
        ttl = min(ttl, settings.REDIS_MAX_CACHE_TTL)

        try:
            if isinstance(value, BaseModel):
                serialized = value.model_dump_json()
            else:
                serialized = json.dumps(value, default=str)

            await client.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {e}")
            return False

    @classmethod
    async def set_model(cls, key: str, model_instance: BaseModel, ttl_seconds: int | None = None) -> bool:
        """Set a Pydantic model instance in Redis cache with mandatory TTL."""
        return await cls.set(key, model_instance, ttl_seconds=ttl_seconds)

    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete a key from Redis cache."""
        client = get_redis_client()
        if client is None:
            return False
        try:
            await client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {e}")
            return False

    @classmethod
    async def exists(cls, key: str) -> bool:
        """Check if a key exists in Redis cache."""
        client = get_redis_client()
        if client is None:
            return False
        try:
            return bool(await client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists error for key '{key}': {e}")
            return False
