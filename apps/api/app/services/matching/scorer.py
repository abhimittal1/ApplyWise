import uuid
import openai
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.job import Job, JobMatch, Skill, job_skills, document_skills
from app.models.document import DocumentChunk
from app.services.ingestion.embeddings import generate_embedding

settings = get_settings()
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# Match component weights (total = 100)
WEIGHTS = {
    "skill_overlap": 0.40,
    "semantic_similarity": 0.30,
    "project_relevance": 0.15,
    "education_fit": 0.10,
    "location_match": 0.05,
}


async def compute_match_score(
    job: Job,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    """
    Compute composite match score for a job against user profile.
    Returns: {score, strong_points, skill_gaps, reasoning, component_scores}
    """
    component_scores = {}

    # 1. Skill Overlap (40%)
    skill_score, matched_skills, missing_skills = await _skill_overlap(job.id, user_id, db)
    component_scores["skill_overlap"] = skill_score

    # 2. Semantic Similarity (30%)
    semantic_score = await _semantic_similarity(job, user_id, db)
    component_scores["semantic_similarity"] = semantic_score

    # 3. Project Relevance (15%)
    project_score, relevant_chunks = await _project_relevance(job, user_id, db)
    component_scores["project_relevance"] = project_score

    # 4. Education Fit (10%) — simplified for MVP
    component_scores["education_fit"] = 50.0  # Placeholder

    # 5. Location Match (5%)
    location_score = _location_match(job)
    component_scores["location_match"] = location_score

    # Weighted total
    total = sum(
        component_scores[k] * WEIGHTS[k] for k in WEIGHTS
    )

    # Generate reasoning
    strong_points = matched_skills[:5]
    skill_gaps = missing_skills[:5]
    reasoning = await _generate_reasoning(
        job, total, strong_points, skill_gaps, component_scores
    )

    return {
        "score": round(total, 1),
        "strong_points": strong_points,
        "skill_gaps": skill_gaps,
        "reasoning": reasoning,
        "component_scores": component_scores,
    }


async def _skill_overlap(
    job_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
) -> tuple[float, list[str], list[str]]:
    """Calculate skill overlap score between user and job."""
    # Get job skills
    result = await db.execute(
        select(Skill.canonical_name).join(job_skills).where(job_skills.c.job_id == job_id)
    )
    job_skill_names = set(row[0] for row in result.fetchall())

    # Get user skills (from documents)
    result = await db.execute(
        select(Skill.canonical_name)
        .join(document_skills)
        .join(
            # Join through documents to filter by user
            __import__('sqlalchemy').text(
                "documents ON document_skills.document_id = documents.id"
            )
        )
    )
    # Simplified: get all user skills via a raw query
    user_result = await db.execute(
        text("""
            SELECT DISTINCT s.canonical_name
            FROM skills s
            JOIN document_skills ds ON s.id = ds.skill_id
            JOIN documents d ON ds.document_id = d.id
            WHERE d.user_id = :user_id
        """),
        {"user_id": str(user_id)},
    )
    user_skill_names = set(row[0] for row in user_result.fetchall())

    if not job_skill_names:
        return 50.0, list(user_skill_names)[:5], []

    matched = job_skill_names & user_skill_names
    missing = job_skill_names - user_skill_names

    score = (len(matched) / len(job_skill_names)) * 100 if job_skill_names else 50.0

    return score, sorted(matched), sorted(missing)


async def _semantic_similarity(
    job: Job, user_id: uuid.UUID, db: AsyncSession
) -> float:
    """Compute semantic similarity between job embedding and user's document embeddings."""
    if job.embedding is None:
        return 50.0

    # Get average of user's chunk embeddings
    result = await db.execute(
        text("""
            SELECT AVG(embedding <=> CAST(:job_embedding AS vector)) as avg_distance
            FROM document_chunks
            WHERE user_id = :user_id AND embedding IS NOT NULL
        """),
        {"job_embedding": str(list(job.embedding)), "user_id": str(user_id)},
    )
    row = result.fetchone()
    if not row or row[0] is None:
        return 50.0

    # Convert distance to similarity score (0-100)
    avg_distance = float(row[0])
    similarity = max(0, (1 - avg_distance)) * 100
    return round(similarity, 1)


async def _project_relevance(
    job: Job, user_id: uuid.UUID, db: AsyncSession
) -> tuple[float, list[str]]:
    """Find most relevant user project chunks for this job."""
    if not job.description:
        return 50.0, []

    try:
        query_embedding = await generate_embedding(job.description[:2000])

        result = await db.execute(
            text("""
                SELECT content, 1 - (embedding <=> CAST(:embedding AS vector)) as similarity
                FROM document_chunks
                WHERE user_id = :user_id AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT 3
            """),
            {"embedding": str(query_embedding), "user_id": str(user_id)},
        )
        rows = result.fetchall()
        if not rows:
            return 30.0, []

        avg_sim = sum(float(r[1]) for r in rows) / len(rows)
        chunks = [r[0][:100] for r in rows]
        return round(avg_sim * 100, 1), chunks
    except Exception:
        return 50.0, []


def _location_match(job: Job) -> float:
    """Simple location matching."""
    if job.remote:
        return 100.0
    if job.location:
        return 60.0  # Non-remote gets baseline
    return 50.0


async def _generate_reasoning(
    job: Job,
    score: float,
    strong_points: list[str],
    skill_gaps: list[str],
    component_scores: dict,
) -> str:
    """Generate natural language reasoning for the match."""
    if not client:
        return f"Match score: {score:.0f}/100. Matching skills: {', '.join(strong_points[:3]) or 'None identified'}. Gaps: {', '.join(skill_gaps[:3]) or 'None identified'}."

    prompt = f"""Write 2-3 sentences explaining why this candidate is a {score:.0f}% match for the {job.title} role at {job.company}.

Strong points: {', '.join(strong_points) or 'None identified'}
Skill gaps: {', '.join(skill_gaps) or 'None'}
Skill overlap score: {component_scores.get('skill_overlap', 0):.0f}/100
Semantic similarity: {component_scores.get('semantic_similarity', 0):.0f}/100

Be specific and actionable."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You provide concise job match analysis. Be direct and helpful."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""
    except Exception:
        return f"Match score: {score:.0f}/100."
