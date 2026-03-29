import uuid
import asyncio
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()

# Local storage directory for MVP (swap to S3 later)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def upload_file(user_id: uuid.UUID, file_content: bytes, filename: str, ext: str) -> str:
    """Store file and return the storage key."""
    file_uuid = uuid.uuid4()
    key = f"users/{user_id}/docs/{file_uuid}.{ext}"
    file_path = UPLOAD_DIR / key

    file_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(file_path.write_bytes, file_content)

    return key


async def download_file(key: str) -> bytes:
    """Download file by storage key."""
    file_path = UPLOAD_DIR / key
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {key}")
    return await asyncio.to_thread(file_path.read_bytes)


async def delete_file(key: str) -> None:
    """Delete file by storage key."""
    file_path = UPLOAD_DIR / key
    if file_path.exists():
        file_path.unlink()
