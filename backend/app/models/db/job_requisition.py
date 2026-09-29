"""
JobRequisition SQLAlchemy ORM Model.
Persists job roles, descriptions, dynamic blueprints, and reviewer-customized question criteria.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

__all__ = ["JobRequisition"]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobRequisition(Base):
    __tablename__ = "job_requisitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    # SHA-256 hash of role_title.lower().strip() + ":" + job_description.strip()
    jd_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    role_title: Mapped[str] = mapped_column(String(255), index=True)
    job_description: Mapped[str] = mapped_column(Text)

    # Serialized EvaluationQuestionsBlueprint JSON
    blueprint_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Recruiter-configured questions JSON (with is_mandatory flags and edited prompts)
    configured_questions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Human-in-the-loop review flag: must be True before candidate evaluations can run
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
