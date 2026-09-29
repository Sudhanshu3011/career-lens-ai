"""
CareerLens AI - Session Repository
Encapsulates all database operations for AnalysisSession entities.
"""

from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.db.session import AnalysisSession


class SessionRepository:
    """Repository layer managing AnalysisSession entity persistence and queries."""

    @staticmethod
    def get_by_id(db: Session, session_id: str) -> Optional[AnalysisSession]:
        return (
            db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        )

    @staticmethod
    def list_recent(db: Session, limit: int = 20) -> List[AnalysisSession]:
        return (
            db.query(AnalysisSession)
            .order_by(AnalysisSession.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        filename: str,
        extracted_text: str,
        job_description: str,
    ) -> AnalysisSession:
        session = AnalysisSession(
            resume_filename=filename,
            extracted_text=extracted_text,
            job_description=job_description.strip(),
            status="pending",
            current_step=1,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def save(db: Session, session: AnalysisSession) -> AnalysisSession:
        db.commit()
        db.refresh(session)
        return session
