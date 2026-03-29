import json
import uuid
import openai
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.job import Job
from app.services.ingestion.embeddings import generate_embedding

settings = get_settings()
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


async def _get_relevant_chunks(job_description: str, user_id: uuid.UUID, db: AsyncSession, limit: int = 5) -> list[str]:
    """Retrieve most relevant user document chunks for a job."""
    try:
        embedding = await generate_embedding(job_description[:2000])
        result = await db.execute(
            text("""
                SELECT content FROM document_chunks
                WHERE user_id = :user_id AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """),
            {"embedding": str(embedding), "user_id": str(user_id), "limit": limit},
        )
        return [row[0] for row in result.fetchall()]
    except Exception:
        return []


async def generate_resume_suggestions(job: Job, user_id: uuid.UUID, db: AsyncSession) -> dict:
    """Generate resume tailoring suggestions for a specific job."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    chunks = await _get_relevant_chunks(job.description or job.title, user_id, db)
    context = "\n---\n".join(chunks) if chunks else "No documents uploaded yet."

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a career coach. Help the user tailor their resume for a specific role. Return valid JSON."},
            {"role": "user", "content": f"""Based on the user's experience and the target job, provide resume tailoring suggestions.

User's Experience:
{context}

Target Job: {job.title} at {job.company}
Job Description: {job.description or 'Not available'}

Return JSON with:
{{
  "emphasize": ["bullet points from their experience to highlight"],
  "new_bullets": ["suggested new bullet points to add"],
  "professional_summary": "A 3-4 sentence role-specific professional summary"
}}"""},
        ],
        max_tokens=1500,
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content or "{}")


async def generate_cover_letter(job: Job, user_id: uuid.UUID, db: AsyncSession) -> str:
    """Generate a tailored cover letter."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    chunks = await _get_relevant_chunks(job.description or job.title, user_id, db)
    context = "\n---\n".join(chunks) if chunks else "No documents uploaded yet."

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You write professional cover letters. Be specific, use evidence from the user's background."},
            {"role": "user", "content": f"""Write a 3-paragraph cover letter for {job.title} at {job.company}.

User's Background:
{context}

Job Description: {job.description or 'Not available'}

Structure:
- Paragraph 1: Hook + role fit
- Paragraph 2: Specific experience evidence (reference actual projects/skills from their documents)
- Paragraph 3: Call to action

Keep it professional, concise, and personalized."""},
        ],
        max_tokens=1000,
        temperature=0.5,
    )

    return response.choices[0].message.content or ""


async def generate_recruiter_email(job: Job, user_id: uuid.UUID, db: AsyncSession) -> str:
    """Generate a recruiter outreach email."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    chunks = await _get_relevant_chunks(job.description or job.title, user_id, db, limit=3)
    context = "\n---\n".join(chunks) if chunks else ""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You write short professional recruiter outreach emails. Be direct and personalized. 150-200 words max."},
            {"role": "user", "content": f"""Write a recruiter outreach email for {job.title} at {job.company}.

User's key experience:
{context}

Job Description: {job.description or 'Not available'}

Include: who they are, what they bring, a clear ask. Professional tone, direct, personalized to the role."""},
        ],
        max_tokens=500,
        temperature=0.5,
    )

    return response.choices[0].message.content or ""


async def generate_skill_roadmap(job: Job, skill_gaps: list[str], db: AsyncSession) -> list[dict]:
    """Generate a learning roadmap for skill gaps."""
    if not client or not skill_gaps:
        return []

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You create actionable learning roadmaps. Return valid JSON."},
            {"role": "user", "content": f"""For the role {job.title} at {job.company}, create a learning roadmap for these skill gaps: {', '.join(skill_gaps)}.

Return JSON array:
[
  {{
    "skill": "skill name",
    "importance": "Why this skill matters for this specific role",
    "resources": ["resource 1", "resource 2"],
    "project_idea": "A small project to demonstrate this skill",
    "estimated_time": "e.g., 1-2 weeks"
  }}
]"""},
        ],
        max_tokens=1500,
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    content = json.loads(response.choices[0].message.content or '{"roadmap": []}')
    return content if isinstance(content, list) else content.get("roadmap", [])
