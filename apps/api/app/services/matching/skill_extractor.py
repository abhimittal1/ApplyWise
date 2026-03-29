import json
import uuid
import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.job import Skill

settings = get_settings()

client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

EXTRACTION_PROMPT = """Extract all technical skills, tools, frameworks, programming languages, and domain knowledge from the following text. Return a JSON array like:
[
  { "name": "Python", "category": "language", "confidence": 0.95 },
  { "name": "Docker", "category": "tool", "confidence": 0.9 },
  { "name": "Machine Learning", "category": "domain", "confidence": 0.85 }
]

Categories: language, framework, tool, database, cloud, domain, methodology, soft_skill
Only return skills that are clearly mentioned. Return valid JSON array only.

Text:
"""

# Canonical name mapping for normalization
SKILL_ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "python3": "Python",
    "python": "Python",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "vue": "Vue.js",
    "angular.js": "Angular",
    "angularjs": "Angular",
    "angular": "Angular",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "next": "Next.js",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "go": "Go",
    "golang": "Go",
}


def normalize_skill_name(name: str) -> str:
    """Normalize a skill name to its canonical form."""
    return SKILL_ALIASES.get(name.lower().strip(), name.strip())


async def extract_skills_from_text(text: str) -> list[dict]:
    """Extract skills from text using LLM."""
    if not client:
        return []

    # Truncate to avoid token limits
    truncated = text[:6000]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract technical skills from text. Always return a valid JSON array."},
                {"role": "user", "content": EXTRACTION_PROMPT + truncated},
            ],
            max_tokens=1000,
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or '{"skills": []}'
        parsed = json.loads(content)

        # Handle both array and object responses
        skills = parsed if isinstance(parsed, list) else parsed.get("skills", [])

        # Normalize names
        for skill in skills:
            skill["name"] = normalize_skill_name(skill.get("name", ""))

        return skills
    except Exception:
        return []


async def get_or_create_skill(
    name: str, category: str, db: AsyncSession
) -> Skill:
    """Get or create a skill record."""
    canonical = normalize_skill_name(name)
    result = await db.execute(
        select(Skill).where(Skill.canonical_name == canonical)
    )
    skill = result.scalar_one_or_none()

    if not skill:
        skill = Skill(
            id=uuid.uuid4(),
            name=canonical,
            category=category,
            canonical_name=canonical,
        )
        db.add(skill)
        await db.flush()

    return skill
