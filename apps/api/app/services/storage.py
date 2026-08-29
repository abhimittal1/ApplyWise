import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain; charset=utf-8",
}


def _get_s3_client():
    """Lazily construct S3 client with optional endpoint overrides."""
    import boto3
    from botocore.config import Config

    kwargs = {
        "region_name": settings.S3_REGION or "us-east-1",
        "config": Config(retries={"max_attempts": 3, "mode": "standard"}),
    }
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    if settings.S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

    return boto3.client("s3", **kwargs)


def _upload_s3_sync(key: str, file_content: bytes, content_type: Optional[str] = None) -> None:
    client = _get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type
    client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=file_content,
        **extra_args,
    )


def _download_s3_sync(key: str) -> bytes:
    import botocore.exceptions

    client = _get_s3_client()
    try:
        response = client.get_object(Bucket=settings.S3_BUCKET, Key=key)
        return response["Body"].read()
    except client.exceptions.NoSuchKey:
        raise FileNotFoundError(f"File not found in S3: {key}")
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ("NoSuchKey", "404"):
            raise FileNotFoundError(f"File not found in S3: {key}")
        raise


def _delete_s3_sync(key: str) -> None:
    import botocore.exceptions

    client = _get_s3_client()
    try:
        client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
    except botocore.exceptions.ClientError as e:
        logger.warning(f"Failed to delete S3 object {key}: {e}")


async def upload_file(user_id: uuid.UUID, file_content: bytes, filename: str, ext: str) -> str:
    """Store file in S3 (if configured) or local disk and return storage key."""
    file_uuid = uuid.uuid4()
    # Sanitize extension to prevent dot-dot or path injection
    clean_ext = ext.lstrip(".").replace("/", "").replace("\\", "")
    key = f"users/{user_id}/docs/{file_uuid}.{clean_ext}"

    if settings.S3_BUCKET:
        content_type = CONTENT_TYPES.get(clean_ext.lower(), "application/octet-stream")
        await asyncio.to_thread(_upload_s3_sync, key, file_content, content_type)
        return key

    # Local fallback
    base_dir = UPLOAD_DIR.resolve()
    file_path = (UPLOAD_DIR / key).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Invalid storage path")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(file_path.write_bytes, file_content)

    return key


async def download_file(key: str) -> bytes:
    """Download file by storage key from S3 (if configured) or local disk."""
    if settings.S3_BUCKET:
        return await asyncio.to_thread(_download_s3_sync, key)

    # Local fallback
    base_dir = UPLOAD_DIR.resolve()
    file_path = (UPLOAD_DIR / key).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Path traversal detected")
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {key}")
    return await asyncio.to_thread(file_path.read_bytes)


async def delete_file(key: str) -> None:
    """Delete file by storage key from S3 (if configured) or local disk."""
    if settings.S3_BUCKET:
        await asyncio.to_thread(_delete_s3_sync, key)
        return

    # Local fallback
    base_dir = UPLOAD_DIR.resolve()
    file_path = (UPLOAD_DIR / key).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Path traversal detected")
    if file_path.exists():
        file_path.unlink()
