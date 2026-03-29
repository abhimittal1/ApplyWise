import uuid
import logging
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk, DocumentStatus
from app.services.storage import download_file
from app.services.ingestion.extractor import extract_text
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.embeddings import generate_embeddings_batch

logger = logging.getLogger(__name__)


async def process_document(document_id: uuid.UUID, db: AsyncSession) -> None:
    """
    Full document processing pipeline:
    1. Download file from storage
    2. Extract text
    3. Chunk text
    4. Generate embeddings
    5. Store chunks with embeddings
    """
    # Get document
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        logger.error(f"Document {document_id} not found")
        return

    try:
        # Update status
        doc.status = DocumentStatus.PROCESSING
        await db.flush()

        # 1. Download file
        file_content = await download_file(doc.s3_key)

        # 2. Extract text (CPU-bound, run in thread pool)
        extracted = await asyncio.to_thread(extract_text, file_content, doc.file_type)
        doc.extracted_text = extracted
        await db.flush()

        if not extracted.strip():
            doc.status = DocumentStatus.FAILED
            await db.flush()
            logger.warning(f"Document {document_id}: no text extracted")
            return

        # 3. Chunk text (CPU-bound, run in thread pool)
        chunks = await asyncio.to_thread(chunk_text, extracted, 512, 64)

        if not chunks:
            doc.status = DocumentStatus.FAILED
            await db.flush()
            logger.warning(f"Document {document_id}: no chunks generated")
            return

        # 4. Generate embeddings (async OpenAI call)
        chunk_texts = [c["content"] for c in chunks]
        embeddings = await generate_embeddings_batch(chunk_texts)

        # 5. Store chunks
        for chunk_data, embedding in zip(chunks, embeddings):
            chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=doc.id,
                user_id=doc.user_id,
                content=chunk_data["content"],
                chunk_index=chunk_data["chunk_index"],
                embedding=embedding,
                metadata_={
                    "document_id": str(doc.id),
                    "filename": doc.filename,
                    "chunk_index": chunk_data["chunk_index"],
                    "token_count": chunk_data["token_count"],
                },
            )
            db.add(chunk)

        doc.status = DocumentStatus.READY
        await db.flush()
        logger.info(f"Document {document_id}: processed {len(chunks)} chunks")

    except Exception as e:
        doc.status = DocumentStatus.FAILED
        await db.flush()
        logger.error(f"Document {document_id} processing failed: {e}")
        raise
