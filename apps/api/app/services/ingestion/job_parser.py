import json
import openai
from app.core.config import get_settings

settings = get_settings()

client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

PARSE_PROMPT = """Extract the following structured information from this job description. Return valid JSON only:
{
  "title": "Job Title",
  "company": "Company Name",
  "location": "Location or Remote",
  "description": "Brief summary of the role (2-3 sentences)",
  "requirements": ["requirement 1", "requirement 2", ...]
}

If a field is not found, use null. For requirements, extract key skills, qualifications, and responsibilities.

Job Description:
"""


async def parse_job_text(raw_text: str) -> dict:
    """Parse raw job description text into structured fields using LLM."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract structured job information from text. Always return valid JSON."},
            {"role": "user", "content": PARSE_PROMPT + raw_text},
        ],
        max_tokens=1000,
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


async def parse_job_html(html_text: str) -> dict:
    """Parse HTML content from a job page into structured fields."""
    if not client:
        raise RuntimeError("OpenAI API key not configured")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract structured job information from HTML content. Ignore navigation, ads, and boilerplate. Always return valid JSON."},
            {"role": "user", "content": PARSE_PROMPT + html_text[:8000]},
        ],
        max_tokens=1000,
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)
