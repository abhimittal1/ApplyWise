import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job, JobMatch
from app.models.generated import GeneratedOutput, OutputType
from app.schemas.generate import (
    ResumeSuggestions,
    CoverLetterResponse,
    EmailResponse,
    RoadmapResponse,
    RoadmapItem,
    GeneratedOutputResponse,
)
from app.services.generation.output_generator import (
    generate_resume_suggestions,
    generate_cover_letter,
    generate_recruiter_email,
    generate_skill_roadmap,
)

router = APIRouter(prefix="/generate", tags=["generate"])


async def _get_job(job_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Job:
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/resume-suggestions/{job_id}", response_model=ResumeSuggestions)
async def get_resume_suggestions(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await _get_job(job_id, current_user.id, db)
    suggestions = await generate_resume_suggestions(job, current_user.id, db)

    # Save output
    output = GeneratedOutput(
        id=uuid.uuid4(),
        job_id=job.id,
        user_id=current_user.id,
        output_type=OutputType.RESUME_SUGGESTIONS,
        content=str(suggestions),
    )
    db.add(output)

    return ResumeSuggestions(**suggestions)


@router.post("/cover-letter/{job_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await _get_job(job_id, current_user.id, db)
    content = await generate_cover_letter(job, current_user.id, db)

    output = GeneratedOutput(
        id=uuid.uuid4(),
        job_id=job.id,
        user_id=current_user.id,
        output_type=OutputType.COVER_LETTER,
        content=content,
    )
    db.add(output)

    return CoverLetterResponse(content=content, job_id=job.id)


@router.post("/recruiter-email/{job_id}", response_model=EmailResponse)
async def get_recruiter_email(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await _get_job(job_id, current_user.id, db)
    content = await generate_recruiter_email(job, current_user.id, db)

    output = GeneratedOutput(
        id=uuid.uuid4(),
        job_id=job.id,
        user_id=current_user.id,
        output_type=OutputType.RECRUITER_EMAIL,
        content=content,
    )
    db.add(output)

    return EmailResponse(content=content, job_id=job.id)


@router.post("/roadmap/{job_id}", response_model=RoadmapResponse)
async def get_roadmap(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await _get_job(job_id, current_user.id, db)

    # Get skill gaps from match
    match_result = await db.execute(
        select(JobMatch).where(JobMatch.job_id == job.id)
    )
    match = match_result.scalar_one_or_none()
    skill_gaps = match.skill_gaps if match and match.skill_gaps else []

    items = await generate_skill_roadmap(job, skill_gaps, db)

    output = GeneratedOutput(
        id=uuid.uuid4(),
        job_id=job.id,
        user_id=current_user.id,
        output_type=OutputType.ROADMAP,
        content=str(items),
    )
    db.add(output)

    return RoadmapResponse(
        items=[RoadmapItem(**item) if isinstance(item, dict) else item for item in items],
        job_id=job.id,
    )


@router.get("/history/{job_id}", response_model=list[GeneratedOutputResponse])
async def get_generation_history(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GeneratedOutput)
        .where(
            GeneratedOutput.job_id == job_id,
            GeneratedOutput.user_id == current_user.id,
        )
        .order_by(GeneratedOutput.created_at.desc())
    )
    return result.scalars().all()
