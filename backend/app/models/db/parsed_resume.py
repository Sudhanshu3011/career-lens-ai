"""
ParsedResume SQLAlchemy ORM Model.
Persists structured 6-section candidate data keyed by PDF SHA-256 file hash for instant deduplication.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

__all__ = ["ParsedResume"]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ParsedResume(Base):
    __tablename__ = "parsed_resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    # SHA-256 hash of PDF file bytes for instant deduplication
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), default="resume.pdf")
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Status: 'queued', 'parsing', 'completed', 'failed', 'cached'
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)

    raw_text: Mapped[str] = mapped_column(Text, default="")
    portfolio_links_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Serialized ResumeParsedSections Pydantic model
    parsed_sections_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
