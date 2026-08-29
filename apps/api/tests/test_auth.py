import unittest
import uuid

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)

settings = get_settings()


class TestAuthSecurity(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        """Verify password hashing creates unique salts and verifies accurately."""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_bcrypt_72_byte_truncation_handling(self):
        """Verify long passwords (>72 bytes) are safely handled and verified."""
        long_pwd = "A" * 100
        hashed = hash_password(long_pwd)
        self.assertTrue(verify_password(long_pwd, hashed))
        different_long_pwd = "B" + ("A" * 99)
        self.assertFalse(verify_password(different_long_pwd, hashed))

    def test_access_token_creation_and_decoding(self):
        """Verify JWT access token encodes claims with proper issuer and audience."""
        user_id = uuid.uuid4()
        token = create_access_token(user_id=user_id)
        self.assertIsInstance(token, str)

        payload = decode_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), str(user_id))
        self.assertEqual(payload.get("type"), "access")
        self.assertEqual(payload.get("iss"), settings.JWT_ISSUER)
        self.assertEqual(payload.get("aud"), settings.JWT_AUDIENCE)

    def test_refresh_token_creation_and_hashing(self):
        """Verify refresh tokens are JWT encoded and SHA-256 hashed for at-rest storage."""
        user_id = uuid.uuid4()
        token_str, expires_at = create_refresh_token(user_id=user_id)
        self.assertIsInstance(token_str, str)
        self.assertIsNotNone(expires_at)

        hashed = hash_token(token_str)
        self.assertEqual(len(hashed), 64)  # 32 bytes hex SHA-256

        # Ensure different tokens produce different hashes
        token_str_2, _ = create_refresh_token(user_id=user_id)
        self.assertNotEqual(token_str, token_str_2)
        self.assertNotEqual(hashed, hash_token(token_str_2))


if __name__ == "__main__":
    unittest.main()
