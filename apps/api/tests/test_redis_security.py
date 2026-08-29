import unittest
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel
from starlette.requests import Request

from app.core.rate_limit import (
    BoundedMemoryRateLimitStore,
    _get_client_ip,
    format_rate_limit_key,
)
from app.core.cache import CacheService
from app.workers.celery_app import celery_app
from app.workers.document_tasks import process_document_task


class SampleModel(BaseModel):
    id: str
    name: str
    count: int


def create_mock_request(client_ip="127.0.0.1", headers=None):
    scope = {
        "type": "http",
        "client": (client_ip, 12345),
        "headers": [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()],
    }
    return Request(scope)


class TestRedisSecurity(unittest.TestCase):
    def test_trusted_proxy_ip_extraction_from_untrusted_client(self):
        """Verify that untrusted direct client IP cannot spoof client IP via headers."""
        req = create_mock_request(
            client_ip="198.51.100.25",  # Public / untrusted IP
            headers={"X-Forwarded-For": "203.0.113.195", "CF-Connecting-IP": "203.0.113.199"},
        )
        self.assertEqual(_get_client_ip(req), "198.51.100.25")

    def test_trusted_proxy_ip_extraction_from_trusted_client(self):
        """Verify that trusted proxy IP allows reading client IP from headers."""
        req_cf = create_mock_request(
            client_ip="127.0.0.1",  # In TRUSTED_PROXIES
            headers={"CF-Connecting-IP": "203.0.113.50"},
        )
        self.assertEqual(_get_client_ip(req_cf), "203.0.113.50")

        req_xff = create_mock_request(
            client_ip="127.0.0.1",
            headers={"X-Forwarded-For": "203.0.113.75, 10.0.0.1"},
        )
        self.assertEqual(_get_client_ip(req_xff), "203.0.113.75")

    def test_rate_limit_key_namespacing(self):
        """Verify Redis rate limit keys have strict application and environment namespacing."""
        key = format_rate_limit_key("ai_chat", "user-uuid-123")
        self.assertTrue(key.startswith("applywise:"))
        self.assertIn(":rate_limit:ai_chat:user-uuid-123", key)

    def test_bounded_memory_rate_limit_store_eviction(self):
        """Verify bounded memory rate limiter bounds max keys to prevent memory exhaustion DoS."""
        store = BoundedMemoryRateLimitStore(max_keys=3)
        now = 1000.0

        # Insert 3 keys
        self.assertFalse(store.record_and_check("key1", now, window_seconds=60, limit=5))
        self.assertFalse(store.record_and_check("key2", now, window_seconds=60, limit=5))
        self.assertFalse(store.record_and_check("key3", now, window_seconds=60, limit=5))
        self.assertEqual(len(store._buckets), 3)

        # Insert 4th key -> oldest key (key1) is evicted
        self.assertFalse(store.record_and_check("key4", now, window_seconds=60, limit=5))
        self.assertEqual(len(store._buckets), 3)
        self.assertNotIn("key1", store._buckets)
        self.assertIn("key4", store._buckets)

    def test_bounded_memory_rate_limit_exceeded(self):
        """Verify sliding window limit check functions accurately in memory."""
        store = BoundedMemoryRateLimitStore(max_keys=10)
        now = 1000.0

        # Limit = 2 requests
        self.assertFalse(store.record_and_check("test_key", now, window_seconds=60, limit=2))
        self.assertFalse(store.record_and_check("test_key", now + 1, window_seconds=60, limit=2))
        # 3rd request exceeds limit
        self.assertTrue(store.record_and_check("test_key", now + 2, window_seconds=60, limit=2))

    def test_cache_service_key_formatting(self):
        """Verify CacheService strictly namespaces keys by environment and tenant."""
        key = CacheService.format_key(namespace="job_matches", tenant_id="user_abc", resource_id="job_xyz")
        self.assertTrue(key.startswith("applywise:"))
        self.assertIn(":job_matches:user_abc:job_xyz", key)

    def test_celery_worker_security_configuration(self):
        """Verify Celery task queue configurations enforce secure serialization and TTLs."""
        conf = celery_app.conf
        self.assertEqual(conf.task_serializer, "json")
        self.assertEqual(conf.accept_content, ["json"])
        self.assertEqual(conf.result_serializer, "json")
        self.assertEqual(conf.result_expires, 3600)
        self.assertTrue(conf.task_default_queue.startswith("applywise_"))
        self.assertTrue(process_document_task.ignore_result)


class TestAsyncCacheService(unittest.IsolatedAsyncioTestCase):
    async def test_cache_service_set_and_get_with_pydantic(self):
        """Verify CacheService uses pure JSON serialization with mandatory TTL and Pydantic validation."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = '{"id": "item_1", "name": "Test Item", "count": 42}'
        mock_redis.set.return_value = True

        with patch("app.core.cache.get_redis_client", return_value=mock_redis):
            model = await CacheService.get_model("test_key", SampleModel)
            self.assertIsNotNone(model)
            self.assertEqual(model.id, "item_1")
            self.assertEqual(model.name, "Test Item")
            self.assertEqual(model.count, 42)

            instance = SampleModel(id="item_2", name="New Item", count=100)
            success = await CacheService.set_model("test_key_2", instance, ttl_seconds=300)
            self.assertTrue(success)
            mock_redis.set.assert_called_once()
            args, kwargs = mock_redis.set.call_args
            self.assertEqual(args[0], "test_key_2")
            self.assertEqual(kwargs["ex"], 300)

    async def test_cache_service_mandatory_ttl_validation(self):
        """Verify CacheService rejects non-positive TTLs."""
        mock_redis = AsyncMock()
        with patch("app.core.cache.get_redis_client", return_value=mock_redis):
            with self.assertRaises(ValueError):
                await CacheService.set("test_key", {"data": 1}, ttl_seconds=0)

            with self.assertRaises(ValueError):
                await CacheService.set("test_key", {"data": 1}, ttl_seconds=-10)


if __name__ == "__main__":
    unittest.main()
