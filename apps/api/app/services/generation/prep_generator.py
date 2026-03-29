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


async def generate_prep_questions(job: Job, user_id: uuid.UUID, db: AsyncSession) -> dict:
    """Generate interview prep questions tailored to the job and user profile."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    # Get user context
    user_chunks = []
    if job.description:
        try:
            embedding = await generate_embedding(job.description[:2000])
            result = await db.execute(
                text("""
                    SELECT content FROM document_chunks
                    WHERE user_id = :user_id AND embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT 4
                """),
                {"embedding": str(embedding), "user_id": str(user_id)},
            )
            user_chunks = [row[0] for row in result.fetchall()]
        except Exception:
            pass

    user_context = "\n---\n".join(user_chunks) if user_chunks else "No profile data available."

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You generate interview preparation content. Return valid JSON."},
            {"role": "user", "content": f"""Generate interview prep for {job.title} at {job.company}.

Job Description: {job.description or 'Not available'}

Candidate Background:
{user_context}

Return JSON:
{{
  "technical": [
    {{"category": "technical", "question": "...", "suggested_answer": "brief answer scaffold using candidate's experience", "difficulty": "medium"}}
  ],
  "behavioral": [
    {{"category": "behavioral", "question": "Tell me about a time when...", "suggested_answer": "STAR format scaffold using candidate's projects", "difficulty": "medium"}}
  ],
  "system_design": [
    {{"category": "system_design", "question": "Design a...", "suggested_answer": "Key topics to cover", "difficulty": "hard"}}
  ]
}}

Generate 3-4 questions per category. For behavioral questions, use the candidate's actual experience to draft STAR-format answer scaffolds. For system design, extract signals from the job description."""},
        ],
        max_tokens=2500,
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content or '{"technical":[],"behavioral":[],"system_design":[]}')
