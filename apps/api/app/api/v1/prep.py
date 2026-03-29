import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.generated import GeneratedOutput, OutputType
from app.schemas.prep import PrepResponse, PrepQuestion
from app.services.generation.prep_generator import generate_prep_questions

router = APIRouter(prefix="/prep", tags=["prep"])


@router.post("/questions/{job_id}", response_model=PrepResponse)
async def get_prep_questions(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    questions = await generate_prep_questions(job, current_user.id, db)

    # Save output
    output = GeneratedOutput(
        id=uuid.uuid4(),
        job_id=job.id,
        user_id=current_user.id,
        output_type=OutputType.INTERVIEW_QUESTIONS,
        content=str(questions),
    )
    db.add(output)

    return PrepResponse(
        job_id=job.id,
        technical=[PrepQuestion(**q) for q in questions.get("technical", [])],
        behavioral=[PrepQuestion(**q) for q in questions.get("behavioral", [])],
        system_design=[PrepQuestion(**q) for q in questions.get("system_design", [])],
    )
