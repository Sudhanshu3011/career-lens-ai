import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Status: 'pending', 'parsed', 'skills_extracted', 'decision_computed', 'completed', 'failed'
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    current_step: Mapped[int] = mapped_column(Integer, default=1)

    resume_filename: Mapped[str] = mapped_column(String(255), default="resume.pdf")
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    job_description: Mapped[str] = mapped_column(Text, default="")

    # JSON-encoded step results
    parsed_sections_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills_data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    laya_decision_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    jobs_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

