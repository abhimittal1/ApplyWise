import uuid
from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: uuid.UUID | None = None


class SourceChunk(BaseModel):
    chunk_id: str
    content: str
    filename: str | None = None
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    conversation_id: uuid.UUID


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    sources: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
