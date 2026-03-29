import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job, JobMatch
from app.services.matching.scorer import compute_match_score

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/jobs/{job_id}/match")
async def match_job(
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

    # Check cache
    cached = await db.execute(
        select(JobMatch).where(JobMatch.job_id == job_id)
    )
    existing = cached.scalar_one_or_none()
    if existing:
        return {
            "score": existing.score,
            "strong_points": existing.strong_points,
            "skill_gaps": existing.skill_gaps,
            "reasoning": existing.reasoning,
            "component_scores": existing.component_scores,
        }

    # Compute fresh
    match_result = await compute_match_score(job, current_user.id, db)

    # Cache result
    match_record = JobMatch(
        id=uuid.uuid4(),
        job_id=job.id,
        user_id=current_user.id,
        score=match_result["score"],
        strong_points=match_result["strong_points"],
        skill_gaps=match_result["skill_gaps"],
        reasoning=match_result["reasoning"],
        component_scores=match_result["component_scores"],
    )
    db.add(match_record)

    return match_result


@router.post("/jobs/rematch-all")
async def rematch_all_jobs(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Re-score all saved jobs. Runs in background."""
    background_tasks.add_task(_rematch_all, current_user.id)
    return {"message": "Re-matching all jobs in background"}


async def _rematch_all(user_id: uuid.UUID):
    from app.core.database import async_session_factory

    async with async_session_factory() as session:
        try:
            # Delete existing matches
            result = await session.execute(
                select(JobMatch).where(JobMatch.user_id == user_id)
            )
            for match in result.scalars().all():
                await session.delete(match)
            await session.flush()

            # Re-score all jobs
            jobs_result = await session.execute(
                select(Job).where(Job.user_id == user_id)
            )
            for job in jobs_result.scalars().all():
                try:
                    match_result = await compute_match_score(job, user_id, session)
                    record = JobMatch(
                        id=uuid.uuid4(),
                        job_id=job.id,
                        user_id=user_id,
                        score=match_result["score"],
                        strong_points=match_result["strong_points"],
                        skill_gaps=match_result["skill_gaps"],
                        reasoning=match_result["reasoning"],
                        component_scores=match_result["component_scores"],
                    )
                    session.add(record)
                except Exception:
                    continue

            await session.commit()
        except Exception:
            await session.rollback()
