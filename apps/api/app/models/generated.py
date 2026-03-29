import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum


class OutputType(str, enum.Enum):
    RESUME_SUGGESTIONS = "RESUME_SUGGESTIONS"
    COVER_LETTER = "COVER_LETTER"
    RECRUITER_EMAIL = "RECRUITER_EMAIL"
    ROADMAP = "ROADMAP"
    INTERVIEW_QUESTIONS = "INTERVIEW_QUESTIONS"


class GeneratedOutput(Base):
    __tablename__ = "generated_outputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    output_type: Mapped[OutputType] = mapped_column(SAEnum(OutputType), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
