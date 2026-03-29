import uuid
from pydantic import BaseModel


class PrepRequest(BaseModel):
    job_id: uuid.UUID


class PrepQuestion(BaseModel):
    category: str  # technical, behavioral, role_specific
    question: str
    suggested_answer: str | None = None
    difficulty: str | None = None


class PrepResponse(BaseModel):
    job_id: uuid.UUID
    technical: list[PrepQuestion]
    behavioral: list[PrepQuestion]
    system_design: list[PrepQuestion]
