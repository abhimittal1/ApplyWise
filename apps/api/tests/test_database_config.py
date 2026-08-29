import unittest

from app.core.config import Settings


class TestDatabaseConfig(unittest.TestCase):
    def test_database_url_normalization_postgres_prefix(self):
        """Ensure postgres:// is converted to postgresql+asyncpg:// for async engine."""
        settings = Settings(
            DATABASE_URL="postgres://user:pass@ep-cool-db.us-east-1.aws.neon.tech/dbname",
            SECRET_KEY="test-secret-key-12345",
        )
        self.assertTrue(settings.DATABASE_URL.startswith("postgresql+asyncpg://"))
        self.assertIn("user:pass@ep-cool-db.us-east-1.aws.neon.tech/dbname", settings.DATABASE_URL)

    def test_database_url_normalization_postgresql_prefix(self):
        """Ensure postgresql:// is converted to postgresql+asyncpg://."""
        settings = Settings(
            DATABASE_URL="postgresql://user:pass@dpg-render-db.render.com/dbname",
            SECRET_KEY="test-secret-key-12345",
        )
        self.assertTrue(settings.DATABASE_URL.startswith("postgresql+asyncpg://"))
        self.assertIn("user:pass@dpg-render-db.render.com/dbname", settings.DATABASE_URL)

    def test_database_url_sslmode_conversion_for_asyncpg(self):
        """Ensure sslmode query parameters are converted to ssl for asyncpg."""
        settings = Settings(
            DATABASE_URL="postgres://user:pass@db.supabase.co:5432/postgres?sslmode=require",
            SECRET_KEY="test-secret-key-12345",
        )
        self.assertTrue(settings.DATABASE_URL.startswith("postgresql+asyncpg://"))
        self.assertIn("ssl=require", settings.DATABASE_URL)
        self.assertNotIn("sslmode=require", settings.DATABASE_URL)

    def test_database_url_sync_auto_derivation_from_async_url(self):
        """Ensure DATABASE_URL_SYNC is automatically derived when DATABASE_URL is set to a cloud DB."""
        settings = Settings(
            DATABASE_URL="postgres://user:pass@ep-render.render.com/production?sslmode=require",
            DATABASE_URL_SYNC="",
            SECRET_KEY="test-secret-key-12345",
        )
        self.assertTrue(settings.DATABASE_URL.startswith("postgresql+asyncpg://"))
        self.assertTrue(settings.DATABASE_URL_SYNC.startswith("postgresql://"))
        self.assertNotIn("asyncpg", settings.DATABASE_URL_SYNC)
        self.assertIn("user:pass@ep-render.render.com/production", settings.DATABASE_URL_SYNC)

    def test_database_url_sync_prefix_normalization(self):
        """Ensure explicit postgres:// DATABASE_URL_SYNC is converted to postgresql:// for sync engine."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@db.cloud.com/app",
            DATABASE_URL_SYNC="postgres://user:pass@db.cloud.com/app",
            SECRET_KEY="test-secret-key-12345",
        )
        self.assertTrue(settings.DATABASE_URL_SYNC.startswith("postgresql://"))
        self.assertFalse(settings.DATABASE_URL_SYNC.startswith("postgres://"))

    def test_database_url_sync_derivation_from_default_localhost(self):
        """Ensure DATABASE_URL_SYNC overrides default localhost if DATABASE_URL is non-localhost."""
        settings = Settings(
            DATABASE_URL="postgres://user:pass@render-postgres.render.com/careeros",
            DATABASE_URL_SYNC="postgresql://postgres:postgres@localhost:5432/careeros",
            SECRET_KEY="test-secret-key-12345",
        )
        self.assertTrue(settings.DATABASE_URL_SYNC.startswith("postgresql://"))
        self.assertNotIn("localhost", settings.DATABASE_URL_SYNC)
        self.assertIn("render-postgres.render.com", settings.DATABASE_URL_SYNC)


if __name__ == "__main__":
    unittest.main()
