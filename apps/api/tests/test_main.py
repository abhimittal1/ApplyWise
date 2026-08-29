import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


class TestAppSmoke(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_app_instance_and_metadata(self):
        """Verify the FastAPI application initializes with expected metadata."""
        self.assertEqual(app.version, "0.1.0")
        self.assertTrue(len(app.routes) > 0)

    def test_session_middleware_present(self):
        """Verify SessionMiddleware and CORSMiddleware are registered in middleware stack."""
        middleware_names = [m.cls.__name__ for m in app.user_middleware]
        self.assertIn("SessionMiddleware", middleware_names)
        self.assertIn("CORSMiddleware", middleware_names)

    def test_root_endpoint(self):
        """Verify GET / returns API metadata and 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertEqual(data["version"], "0.1.0")

    @patch("app.main.check_db_connection", new_callable=AsyncMock)
    @patch("app.main.check_redis_connection", new_callable=AsyncMock)
    def test_health_check_healthy(self, mock_redis_conn, mock_db_conn):
        """Verify GET /api/health returns healthy status when dependencies are up."""
        mock_db_conn.return_value = True
        mock_redis_conn.return_value = True

        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["redis"], "connected")


if __name__ == "__main__":
    unittest.main()
