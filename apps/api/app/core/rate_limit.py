import ipaddress
import logging
import time
from collections import OrderedDict
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from app.core.config import get_settings
from app.core.security import decode_token

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_pool: ConnectionPool | None = None
_redis_client: aioredis.Redis | None = None


def get_redis_pool() -> ConnectionPool | None:
    """Get or create singleton async Redis connection pool with TLS and security parameters."""
    global _redis_pool
    if _redis_pool is None and settings.REDIS_URL:
        try:
            kwargs: dict = {
                "max_connections": settings.REDIS_MAX_CONNECTIONS,
                "socket_timeout": settings.REDIS_SOCKET_TIMEOUT,
                "socket_connect_timeout": settings.REDIS_CONNECT_TIMEOUT,
                "decode_responses": True,
            }
            if settings.REDIS_URL.startswith("rediss://"):
                kwargs["ssl_cert_reqs"] = "required" if settings.REDIS_SSL_VERIFY else "none"

            _redis_pool = ConnectionPool.from_url(settings.REDIS_URL, **kwargs)
        except Exception as e:
            logger.warning(f"Could not initialize Redis connection pool: {e}")
            _redis_pool = None
    return _redis_pool


def get_redis_client() -> aioredis.Redis | None:
    """Get singleton async Redis client reusing connection pool."""
    global _redis_client
    if _redis_client is None:
        pool = get_redis_pool()
        if pool is not None:
            _redis_client = aioredis.Redis(connection_pool=pool)
    return _redis_client


async def close_redis_client() -> None:
    """Gracefully close Redis client and pool connections."""
    global _redis_client, _redis_pool
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
        except Exception as e:
            logger.warning(f"Error closing Redis client: {e}")
        _redis_client = None
    if _redis_pool is not None:
        try:
            await _redis_pool.aclose()
        except Exception as e:
            logger.warning(f"Error closing Redis connection pool: {e}")
        _redis_pool = None


async def check_redis_connection() -> bool:
    """Check if Redis is accessible and responding to ping."""
    client = get_redis_client()
    if client is None:
        return False
    try:
        return bool(await client.ping())
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


class BoundedMemoryRateLimitStore:
    """
    Memory-bounded LRU store for sliding-window rate limiting fallback.
    Prevents memory exhaustion DoS by capping max keys and evicting expired entries.
    """

    def __init__(self, max_keys: int = 10000):
        self.max_keys = max_keys
        self._buckets: OrderedDict[str, list[float]] = OrderedDict()

    def record_and_check(self, key: str, now: float, window_seconds: float, limit: int) -> bool:
        window_start = now - window_seconds

        if key in self._buckets:
            timestamps = self._buckets.pop(key)
            timestamps = [ts for ts in timestamps if ts > window_start]
        else:
            timestamps = []
            if len(self._buckets) >= self.max_keys:
                # Evict oldest entry (LRU)
                self._buckets.popitem(last=False)

        timestamps.append(now)
        self._buckets[key] = timestamps
        return len(timestamps) > limit

    def clear(self) -> None:
        self._buckets.clear()


_memory_store = BoundedMemoryRateLimitStore(max_keys=10000)


def _is_valid_ip(ip_str: str) -> bool:
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def _get_client_ip(request: Request) -> str:
    """
    Extract client IP with verification against trusted proxies.
    Prevents header injection and IP spoofing attacks.
    """
    direct_ip = request.client.host if request.client else "127.0.0.1"

    is_trusted_proxy = direct_ip in settings.TRUSTED_PROXIES

    if is_trusted_proxy:
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip and _is_valid_ip(cf_ip.strip()):
            return cf_ip.strip()

        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            for ip in x_forwarded_for.split(","):
                cleaned = ip.strip()
                if _is_valid_ip(cleaned):
                    return cleaned

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip and _is_valid_ip(x_real_ip.strip()):
            return x_real_ip.strip()

    return direct_ip


def format_rate_limit_key(name: str, identifier: str) -> str:
    """Format Redis key with strict environment and application namespace to prevent key collisions."""
    env = settings.ENVIRONMENT.lower()
    return f"applywise:{env}:rate_limit:{name}:{identifier}"


class RateLimiter:
    """
    Sliding window rate limiter supporting Redis with bounded in-memory fallback.
    Identifies clients by authenticated user UUID, or verified client IP for unauthenticated requests.
    Prevents token exhaustion, denial of wallet, and abusive request spikes.
    """

    def __init__(self, requests_per_window: int = 20, window_seconds: int = 60, name: str = "default"):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.name = name

    async def __call__(self, request: Request) -> None:
        identifier = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = decode_token(token)
                identifier = payload.get("sub")
            except Exception:
                pass

        if not identifier:
            identifier = _get_client_ip(request)

        rate_limit_key = format_rate_limit_key(self.name, identifier)
        now = time.time()
        window_start = now - self.window_seconds

        client = get_redis_client()
        if client:
            try:
                pipeline = client.pipeline()
                pipeline.zremrangebyscore(rate_limit_key, 0, window_start)
                pipeline.zadd(rate_limit_key, {str(now): now})
                pipeline.zcard(rate_limit_key)
                pipeline.expire(rate_limit_key, int(self.window_seconds + 5))
                _, _, current_count, _ = await pipeline.execute()

                if current_count > self.requests_per_window:
                    retry_after = int(self.window_seconds)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded for {self.name}. Max {self.requests_per_window} requests per {self.window_seconds}s.",
                        headers={"Retry-After": str(retry_after)},
                    )
                return
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"Redis rate limiting failed, falling back to memory: {e}")

        # In-memory sliding window fallback with bounded LRU protection
        exceeded = _memory_store.record_and_check(
            rate_limit_key, now, self.window_seconds, self.requests_per_window
        )
        if exceeded:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {self.name}. Max {self.requests_per_window} requests per {self.window_seconds}s.",
                headers={"Retry-After": str(self.window_seconds)},
            )


# Pre-configured rate limiters
auth_rate_limiter = RateLimiter(requests_per_window=10, window_seconds=60, name="auth")
upload_rate_limiter = RateLimiter(requests_per_window=10, window_seconds=60, name="doc_upload")
job_search_rate_limiter = RateLimiter(requests_per_window=15, window_seconds=60, name="job_search")
job_import_rate_limiter = RateLimiter(requests_per_window=20, window_seconds=60, name="job_import")
job_create_rate_limiter = RateLimiter(requests_per_window=30, window_seconds=60, name="job_create")
chat_rate_limiter = RateLimiter(requests_per_window=30, window_seconds=60, name="ai_chat")
generation_rate_limiter = RateLimiter(requests_per_window=15, window_seconds=60, name="ai_generation")
matching_rate_limiter = RateLimiter(requests_per_window=20, window_seconds=60, name="ai_matching")
ingestion_rate_limiter = RateLimiter(requests_per_window=10, window_seconds=60, name="ai_ingestion")
