import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailResponse(DocumentResponse):
    extracted_text: str | None = None
    chunk_count: int = 0


class DocumentStatusResponse(BaseModel):
    id: uuid.UUID
    status: DocumentStatus
    filename: str
