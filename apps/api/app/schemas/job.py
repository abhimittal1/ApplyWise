import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field, HttpUrl
from app.models.job import JobSource


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=30000)
    url: str | None = Field(None, max_length=2048)
    remote: bool = False
    job_type: str | None = Field(None, max_length=50)
    posted_at: date | None = None
    deadline: date | None = None


class JobImportText(BaseModel):
    raw_text: str = Field(..., min_length=10, max_length=30000)


class JobImportURL(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048)


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
    query: str = Field(..., min_length=1, max_length=200)
    location: str = Field("", max_length=200)


class JobSearchResponse(BaseModel):
    results: list[JobPreview]
    total: int
    apis_used: list[str]
