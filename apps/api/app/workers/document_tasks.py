import asyncio
import uuid
import logging
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.document import Document, DocumentStatus
from app.services.ingestion.pipeline import process_document

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
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
        logger.error(f"Document processing task failed for {document_id}: {exc}")
        if self.request.retries >= self.max_retries:
            # Mark document permanently failed on final retry exhaustion
            _mark_failed_sync(document_id)
        raise self.retry(exc=exc)


def _mark_failed_sync(document_id: str):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def _mark():
                async with async_session_factory() as session:
                    res = await session.execute(select(Document).where(Document.id == uuid.UUID(document_id)))
                    doc = res.scalar_one_or_none()
                    if doc:
                        doc.status = DocumentStatus.FAILED
                        await session.commit()
            loop.run_until_complete(_mark())
        finally:
            loop.close()
    except Exception as err:
        logger.error(f"Failed to set status FAILED for {document_id}: {err}")


async def _process(document_id: str):
    async with async_session_factory() as session:
        try:
            await process_document(uuid.UUID(document_id), session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
