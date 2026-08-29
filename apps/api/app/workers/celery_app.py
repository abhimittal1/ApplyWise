import ssl
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "careeros",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

conf_dict = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_acks_late": True,
    "worker_prefetch_multiplier": 1,
}

if settings.REDIS_URL.startswith("rediss://"):
    conf_dict["broker_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}
    conf_dict["redis_backend_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}

celery_app.conf.update(conf_dict)
