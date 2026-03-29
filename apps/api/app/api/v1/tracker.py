import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job, Application, ApplicationStatus
from app.schemas.tracker import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationNoteAdd,
    ContactUpdate,
    ApplicationResponse,
)

router = APIRouter(prefix="/tracker", tags=["tracker"])


def _to_response(app: Application, job: Job | None = None) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        job_id=app.job_id,
        status=app.status,
        applied_at=app.applied_at,
        oa_date=app.oa_date,
        interview_date=app.interview_date,
        offer_date=app.offer_date,
        recruiter_name=app.recruiter_name,
        recruiter_email=app.recruiter_email,
        notes=app.notes,
        created_at=app.created_at,
        job_title=job.title if job else None,
        job_company=job.company if job else None,
    )


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
    )
    return [_to_response(app, job) for app, job in result.all()]


@router.post("", response_model=ApplicationResponse, status_code=201)
async def create_application(
    body: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify job exists and belongs to user
    job_result = await db.execute(
        select(Job).where(Job.id == body.job_id, Job.user_id == current_user.id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if application already exists
    existing = await db.execute(
        select(Application).where(Application.job_id == body.job_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Application already exists for this job")

    app = Application(
        id=uuid.uuid4(),
        job_id=body.job_id,
        user_id=current_user.id,
        status=body.status,
        notes={},
    )
    db.add(app)
    await db.flush()

    return _to_response(app, job)


@router.patch("/{app_id}/status", response_model=ApplicationResponse)
async def update_status(
    app_id: uuid.UUID,
    body: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .where(Application.id == app_id, Application.user_id == current_user.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    app, job = row
    app.status = body.status

    # Auto-set dates
    now = datetime.now(timezone.utc)
    if body.status == ApplicationStatus.APPLIED and not app.applied_at:
        app.applied_at = now
    elif body.status == ApplicationStatus.OA and not app.oa_date:
        app.oa_date = now
    elif body.status == ApplicationStatus.INTERVIEW and not app.interview_date:
        app.interview_date = now
    elif body.status == ApplicationStatus.OFFER and not app.offer_date:
        app.offer_date = now

    return _to_response(app, job)


@router.post("/{app_id}/notes", response_model=ApplicationResponse)
async def add_note(
    app_id: uuid.UUID,
    body: ApplicationNoteAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .where(Application.id == app_id, Application.user_id == current_user.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    app, job = row
    notes = app.notes or {}
    if body.stage not in notes:
        notes[body.stage] = []
    notes[body.stage].append({
        "content": body.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    app.notes = notes
    flag_modified(app, "notes")

    return _to_response(app, job)


@router.put("/{app_id}/contacts", response_model=ApplicationResponse)
async def update_contacts(
    app_id: uuid.UUID,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .where(Application.id == app_id, Application.user_id == current_user.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    app, job = row
    if body.recruiter_name is not None:
        app.recruiter_name = body.recruiter_name
    if body.recruiter_email is not None:
        app.recruiter_email = body.recruiter_email

    return _to_response(app, job)


@router.delete("/{app_id}", status_code=204)
async def delete_application(
    app_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(app)
