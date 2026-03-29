import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.job import ApplicationStatus


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    status: ApplicationStatus = ApplicationStatus.SAVED


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationNoteAdd(BaseModel):
    stage: str
    content: str


class ContactUpdate(BaseModel):
    recruiter_name: str | None = None
    recruiter_email: str | None = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    status: ApplicationStatus
    applied_at: datetime | None = None
    oa_date: datetime | None = None
    interview_date: datetime | None = None
    offer_date: datetime | None = None
    recruiter_name: str | None = None
    recruiter_email: str | None = None
    notes: dict | None = None
    created_at: datetime

    # Job info
    job_title: str | None = None
    job_company: str | None = None

    model_config = {"from_attributes": True}
