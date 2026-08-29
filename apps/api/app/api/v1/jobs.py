import uuid
import logging

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rate_limit import job_create_rate_limiter, job_import_rate_limiter, job_search_rate_limiter
from app.core.ssrf import safe_fetch_url, SSRFValidationError
from app.models.user import User
from app.models.job import Job, JobSource, job_skills as job_skills_table
from app.schemas.job import (
    JobCreate, JobImportText, JobImportURL, JobPreview, JobResponse,
    JobSearchRequest, JobSearchResponse,
)
from app.services.ingestion.job_parser import parse_job_text, parse_job_html
from app.services.ingestion.embeddings import generate_embedding

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)


@router.post("", response_model=JobResponse, status_code=201, dependencies=[Depends(job_create_rate_limiter)])
async def create_job(
    body: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = Job(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=body.title,
        company=body.company,
        location=body.location,
        description=body.description,
        url=body.url,
        source=JobSource.MANUAL,
        remote=body.remote,
        job_type=body.job_type,
        posted_at=body.posted_at,
        deadline=body.deadline,
    )
    db.add(job)
    await db.flush()

    if body.description:
        background_tasks.add_task(_embed_job, job.id, body.description)
        background_tasks.add_task(_extract_job_skills, job.id, body.description)

    return job


@router.post("/import-text", response_model=JobPreview, dependencies=[Depends(job_import_rate_limiter)])
async def import_from_text(
    body: JobImportText,
    current_user: User = Depends(get_current_user),
):
    parsed = await parse_job_text(body.raw_text)
    return JobPreview(
        title=parsed.get("title") or "Untitled",
        company=parsed.get("company") or "Unknown",
        location=parsed.get("location"),
        description=parsed.get("description"),
        requirements=parsed.get("requirements") or [],
    )


@router.post("/import-text/confirm", response_model=JobResponse, status_code=201, dependencies=[Depends(job_create_rate_limiter)])
async def confirm_text_import(
    body: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = Job(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=body.title,
        company=body.company,
        location=body.location,
        description=body.description,
        url=body.url,
        source=JobSource.PASTE,
        remote=body.remote,
        job_type=body.job_type,
        posted_at=body.posted_at,
        deadline=body.deadline,
    )
    db.add(job)
    await db.flush()

    if body.description:
        background_tasks.add_task(_embed_job, job.id, body.description)
        background_tasks.add_task(_extract_job_skills, job.id, body.description)

    return job


@router.post("/import-url", response_model=JobPreview, dependencies=[Depends(job_import_rate_limiter)])
async def import_from_url(
    body: JobImportURL,
    current_user: User = Depends(get_current_user),
):
    try:
        html_text = await safe_fetch_url(body.url)
    except SSRFValidationError as e:
        logger.warning(f"SSRF validation blocked URL '{body.url}': {e}")
        raise HTTPException(status_code=400, detail=f"Invalid or prohibited URL: {e}")
    except httpx.HTTPError as e:
        logger.warning(f"Failed to fetch job URL '{body.url}': {e}")
        raise HTTPException(status_code=400, detail="Could not fetch the URL")
    except Exception as e:
        logger.error(f"Unexpected error fetching job URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the URL")

    soup = BeautifulSoup(html_text, "html.parser")
    # Strip script and style tags to prevent garbage injection into parsing
    for script_or_style in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        script_or_style.extract()

    main = soup.find("main") or soup.find("article") or soup.find("body")
    text_content = main.get_text(separator="\n", strip=True) if main else ""

    if not text_content:
        raise HTTPException(status_code=400, detail="Could not extract readable content from URL")

    parsed = await parse_job_html(text_content)
    return JobPreview(
        title=parsed.get("title") or "Untitled",
        company=parsed.get("company") or "Unknown",
        location=parsed.get("location"),
        description=parsed.get("description"),
        requirements=parsed.get("requirements") or [],
        url=body.url,
    )


@router.post("/import-url/confirm", response_model=JobResponse, status_code=201, dependencies=[Depends(job_create_rate_limiter)])
async def confirm_url_import(
    body: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = Job(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=body.title,
        company=body.company,
        location=body.location,
        description=body.description,
        url=body.url,
        source=JobSource.URL,
        remote=body.remote,
        job_type=body.job_type,
    )
    db.add(job)
    await db.flush()

    if body.description:
        background_tasks.add_task(_embed_job, job.id, body.description)
        background_tasks.add_task(_extract_job_skills, job.id, body.description)

    return job


@router.post("/search", response_model=JobSearchResponse, dependencies=[Depends(job_search_rate_limiter)])
async def search_jobs(
    body: JobSearchRequest,
    current_user: User = Depends(get_current_user),
):
    from app.services.ingestion.job_search import search_all

    results = await search_all(body.query, body.location)
    previews = [
        JobPreview(
            title=r.title,
            company=r.company or "Unknown",
            location=r.location,
            description=r.description,
            requirements=[],
            url=r.url,
        )
        for r in results
    ]
    apis_used = list(set(r.source_api for r in results))
    return JobSearchResponse(results=previews, total=len(previews), apis_used=apis_used)


@router.post("/search/save", response_model=JobResponse, status_code=201, dependencies=[Depends(job_create_rate_limiter)])
async def save_search_result(
    body: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = Job(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=body.title,
        company=body.company,
        location=body.location,
        description=body.description,
        url=body.url,
        source=JobSource.API,
        remote=body.remote,
        job_type=body.job_type,
    )
    db.add(job)
    await db.flush()

    if body.description:
        background_tasks.add_task(_embed_job, job.id, body.description)
        background_tasks.add_task(_extract_job_skills, job.id, body.description)

    return job


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Job)
        .where(Job.user_id == current_user.id)
        .order_by(Job.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
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
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(
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
    await db.delete(job)
    await db.flush()


async def _embed_job(job_id: uuid.UUID, description: str):
    """Generate and store embedding for a job description."""
    from app.core.database import async_session_factory

    try:
        embedding = await generate_embedding(description)
        async with async_session_factory() as session:
            result = await session.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                job.embedding = embedding
                await session.commit()
    except Exception:
        pass


async def _extract_job_skills(job_id: uuid.UUID, description: str):
    """Extract skills from job description and store in job_skills table."""
    from app.core.database import async_session_factory
    from app.services.matching.skill_extractor import extract_skills_from_text, get_or_create_skill

    try:
        skills = await extract_skills_from_text(description)
        if not skills:
            return

        async with async_session_factory() as session:
            for skill_data in skills:
                skill = await get_or_create_skill(
                    skill_data.get("name", ""),
                    skill_data.get("category", "unknown"),
                    session,
                )
                # Check if association already exists
                existing = await session.execute(
                    select(job_skills_table).where(
                        job_skills_table.c.job_id == job_id,
                        job_skills_table.c.skill_id == skill.id,
                    )
                )
                if not existing.first():
                    await session.execute(
                        job_skills_table.insert().values(
                            job_id=job_id,
                            skill_id=skill.id,
                            is_required=True,
                            confidence=skill_data.get("confidence", 0.8),
                        )
                    )
            await session.commit()
    except Exception as e:
        logger.error(f"Skill extraction failed for job {job_id}: {e}")
