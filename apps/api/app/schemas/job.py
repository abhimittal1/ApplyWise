import uuid
from datetime import datetime, date
from pydantic import BaseModel, HttpUrl
from app.models.job import JobSource


class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: str | None = None
    remote: bool = False
    job_type: str | None = None
    posted_at: date | None = None
    deadline: date | None = None


class JobImportText(BaseModel):
    raw_text: str


class JobImportURL(BaseModel):
    url: str


class JobPreview(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    requirements: list[str] = []
    url: str | None = None


class JobResponse(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: str | None = None
    source: JobSource
    remote: bool
    job_type: str | None = None
    posted_at: date | None = None
    deadline: date | None = None
    match_score: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobDetailResponse(JobResponse):
    match_score: float | None = None
    strong_points: list[str] | None = None
    skill_gaps: list[str] | None = None
    reasoning: str | None = None


class JobSearchRequest(BaseModel):
    query: str
    location: str = ""


class JobSearchResponse(BaseModel):
    results: list[JobPreview]
    total: int
    apis_used: list[str]
