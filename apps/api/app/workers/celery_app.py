import ssl
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "careeros",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

env_name = settings.ENVIRONMENT.lower()

conf_dict = {
    # Serialization & Insecure Deserialization Protections
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "event_serializer": "json",
    # Task Queue Namespacing
    "task_default_queue": f"applywise_{env_name}_tasks",
    # TTL & Memory Exhaustion Controls
    "result_expires": 3600,  # 1 hour expiration for task result keys in Redis
    # Worker Reliability
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_acks_late": True,
    "worker_prefetch_multiplier": 1,
}

# SSL / TLS Encryption & Certificate Verification
if settings.REDIS_URL.startswith("rediss://"):
    cert_reqs = ssl.CERT_REQUIRED if settings.REDIS_SSL_VERIFY else ssl.CERT_NONE
    ssl_options = {"ssl_cert_reqs": cert_reqs}
    conf_dict["broker_use_ssl"] = ssl_options
    conf_dict["redis_backend_use_ssl"] = ssl_options

celery_app.conf.update(conf_dict)
