import unittest
from unittest.mock import patch, MagicMock
import uuid
from fastapi import HTTPException

from app.api.v1.documents import validate_file_magic_bytes
from app.services.storage import upload_file, download_file, delete_file


class TestDocumentValidationAndStorage(unittest.IsolatedAsyncioTestCase):
    def test_magic_byte_validation_pdf(self):
        """Verify PDF magic byte validation."""
        valid_pdf = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n..."
        invalid_pdf = b"NOT_A_PDF_FILE_HEADER"

        # Valid should not raise
        validate_file_magic_bytes(valid_pdf, "pdf")

        # Invalid should raise HTTP 400
        with self.assertRaises(HTTPException) as ctx:
            validate_file_magic_bytes(invalid_pdf, "pdf")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_magic_byte_validation_docx(self):
        """Verify DOCX zip container magic byte validation."""
        valid_docx = b"PK\x03\x04\x14\x00\x06\x00..."
        invalid_docx = b"MZ\x90\x00\x03\x00\x00\x00"  # PE executable header

        validate_file_magic_bytes(valid_docx, "docx")

        with self.assertRaises(HTTPException) as ctx:
            validate_file_magic_bytes(invalid_docx, "docx")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_magic_byte_validation_txt(self):
        """Verify TXT file rejects binary null bytes."""
        valid_txt = b"Hello, this is a plain text resume content."
        binary_txt = b"Hello\x00\x00\x01\x02ExecutableBinaryPayload"

        validate_file_magic_bytes(valid_txt, "txt")

        with self.assertRaises(HTTPException) as ctx:
            validate_file_magic_bytes(binary_txt, "txt")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_magic_byte_validation_empty_file(self):
        """Verify empty file raises HTTP 400."""
        with self.assertRaises(HTTPException) as ctx:
            validate_file_magic_bytes(b"", "pdf")
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_local_storage_lifecycle(self):
        """Verify upload, download, and deletion on local storage."""
        user_id = uuid.uuid4()
        content = b"%PDF-1.4 sample content for testing storage"
        
        # Upload
        key = await upload_file(user_id, content, "sample.pdf", "pdf")
        self.assertTrue(key.startswith(f"users/{user_id}/docs/"))
        self.assertTrue(key.endswith(".pdf"))

        # Download
        retrieved = await download_file(key)
        self.assertEqual(retrieved, content)

        # Delete
        await delete_file(key)
        with self.assertRaises(FileNotFoundError):
            await download_file(key)

    async def test_s3_storage_lifecycle_mocked(self):
        """Verify S3 storage branch when S3_BUCKET is configured."""
        user_id = uuid.uuid4()
        content = b"%PDF-1.4 s3 test content"

        mock_s3 = MagicMock()
        mock_s3.get_object.return_value = {"Body": MagicMock(read=lambda: content)}

        with patch("app.services.storage.settings.S3_BUCKET", "test-bucket"):
            with patch("app.services.storage._get_s3_client", return_value=mock_s3):
                key = await upload_file(user_id, content, "s3_sample.pdf", "pdf")
                self.assertTrue(key.startswith(f"users/{user_id}/docs/"))
                mock_s3.put_object.assert_called_once()

                downloaded = await download_file(key)
                self.assertEqual(downloaded, content)
                mock_s3.get_object.assert_called_once()

                await delete_file(key)
                mock_s3.delete_object.assert_called_once()


if __name__ == "__main__":
    unittest.main()
