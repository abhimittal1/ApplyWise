import asyncio
import uuid
import logging

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory
from app.services.ingestion.pipeline import process_document

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: str):
    """Celery task wrapper for document processing."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_process(document_id))
        finally:
            loop.close()
    except Exception as exc:
        logger.error(f"Document processing task failed: {exc}")
        raise self.retry(exc=exc)


async def _process(document_id: str):
    async with async_session_factory() as session:
        try:
            await process_document(uuid.UUID(document_id), session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
