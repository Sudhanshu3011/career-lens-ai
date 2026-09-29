"""
CandidateEvaluation SQLAlchemy ORM Model.
Persists candidate scoring verdicts, fit scores, and speculatively calibrated evaluations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

__all__ = ["CandidateEvaluation"]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_requisitions.id"), index=True)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("parsed_resumes.id"), index=True)

    candidate_name: Mapped[str] = mapped_column(String(255), default="Candidate")
    pipeline: Mapped[str] = mapped_column(String(32), default="laya")

    # Status: 'pending', 'evaluating', 'completed', 'failed'
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)

    fit_score: Mapped[float] = mapped_column(Float, default=0.0)
    verdict: Mapped[str] = mapped_column(String(32), default="HOLD")

    # Serialized CandidateVerdict JSON
    verdict_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
