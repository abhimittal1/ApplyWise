import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentDetailResponse, DocumentStatusResponse
from app.services.storage import upload_file, delete_file
from app.services.ingestion.pipeline import process_document

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"pdf", "docx", "txt"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_TYPES)}",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20MB limit")

    # Upload to storage
    s3_key = await upload_file(current_user.id, content, file.filename, ext)

    # Create document record
    doc = Document(
        id=uuid.uuid4(),
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext,
        s3_key=s3_key,
        status=DocumentStatus.PROCESSING,
    )
    db.add(doc)
    await db.commit()

    # Process in background (document must be committed first so background session can find it)
    background_tasks.add_task(_process_in_background, doc.id)

    return doc


async def _process_in_background(document_id: uuid.UUID):
    """Run document processing in a background task."""
    import logging
    from app.core.database import async_session_factory

    logger = logging.getLogger(__name__)

    async with async_session_factory() as session:
        try:
            await process_document(document_id, session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Background processing failed for {document_id}: {e}")
            # Set FAILED status in a fresh transaction so it persists
            try:
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = DocumentStatus.FAILED
                    await session.commit()
            except Exception:
                await session.rollback()


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get chunk count
    count_result = await db.execute(
        select(func.count()).where(DocumentChunk.document_id == document_id)
    )
    chunk_count = count_result.scalar() or 0

    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        status=doc.status,
        created_at=doc.created_at,
        extracted_text=doc.extracted_text,
        chunk_count=chunk_count,
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentStatusResponse(id=doc.id, status=doc.status, filename=doc.filename)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from storage
    try:
        await delete_file(doc.s3_key)
    except FileNotFoundError:
        pass

    # Delete from DB (cascades to chunks)
    await db.delete(doc)
