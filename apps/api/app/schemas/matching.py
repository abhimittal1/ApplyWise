import uuid
from pydantic import BaseModel


class MatchResponse(BaseModel):
    score: float
    strong_points: list[str]
    skill_gaps: list[str]
    reasoning: str
    component_scores: dict

    model_config = {"from_attributes": True}


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class UserSkillProfile(BaseModel):
    skills: list[SkillResponse]
    total_documents: int
    total_skills: int
