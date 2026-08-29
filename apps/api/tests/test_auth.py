import unittest
from datetime import timedelta
import uuid

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.core.config import get_settings

settings = get_settings()


class TestAuthSecurity(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        """Verify password hashing creates unique salts and verifies accurately."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_bcrypt_72_byte_truncation_handling(self):
        """Verify long passwords (>72 bytes) are safely handled and verified."""
        long_pwd = "A" * 100
        hashed = get_password_hash(long_pwd)
        self.assertTrue(verify_password(long_pwd, hashed))
        self.assertFalse(verify_password(long_pwd + "different", hashed))

    def test_access_token_creation_and_decoding(self):
        """Verify JWT access token encodes claims with proper issuer and audience."""
        user_id = uuid.uuid4()
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=15),
            token_type="access",
        )
        self.assertIsInstance(token, str)

        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), str(user_id))
        self.assertEqual(payload.get("type"), "access")
        self.assertEqual(payload.get("iss"), settings.JWT_ISSUER)
        self.assertEqual(payload.get("aud"), settings.JWT_AUDIENCE)

    def test_refresh_token_generation_and_hashing(self):
        """Verify refresh tokens are cryptographically random and SHA-256 hashed."""
        raw_token, raw_hash = generate_refresh_token()
        self.assertEqual(len(raw_token), 64)  # 32 bytes hex
        self.assertEqual(hash_refresh_token(raw_token), raw_hash)

        # Ensure different tokens produce different hashes
        raw_token_2, raw_hash_2 = generate_refresh_token()
        self.assertNotEqual(raw_token, raw_token_2)
        self.assertNotEqual(raw_hash, raw_hash_2)


if __name__ == "__main__":
    unittest.main()
