import uuid
from datetime import datetime
from pydantic import BaseModel


class ResumeSuggestions(BaseModel):
    emphasize: list[str] = []
    new_bullets: list[str] = []
    professional_summary: str = ""


class CoverLetterResponse(BaseModel):
    content: str
    job_id: uuid.UUID


class EmailResponse(BaseModel):
    content: str
    job_id: uuid.UUID


class RoadmapItem(BaseModel):
    skill: str
    importance: str = ""
    resources: list[str] = []
    project_idea: str = ""
    estimated_time: str = ""


class RoadmapResponse(BaseModel):
    items: list[RoadmapItem]
    job_id: uuid.UUID


class GeneratedOutputResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    output_type: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
