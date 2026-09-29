"""
CareerLens AI - Job Repository
Encapsulates database operations for JobRequisition entities, including SHA-256 hash lookup.
"""

from __future__ import annotations

import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.db.job_requisition import JobRequisition


class JobRepository:
    """Repository layer managing JobRequisition persistence and hash-based caching."""

    @staticmethod
    def compute_hash(role_title: str, job_description: str) -> str:
        """Computes deterministic SHA-256 hash for (role, jd) deduplication."""
        normalized = f"{role_title.lower().strip()}:{job_description.strip()}"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def get_by_id(db: Session, job_id: str) -> Optional[JobRequisition]:
        return db.query(JobRequisition).filter(JobRequisition.id == job_id).first()

    @staticmethod
    def get_by_hash(db: Session, jd_hash: str) -> Optional[JobRequisition]:
        return db.query(JobRequisition).filter(JobRequisition.jd_hash == jd_hash).first()

    @staticmethod
    def create(
        db: Session,
        role_title: str,
        job_description: str,
        blueprint_json: Optional[str] = None,
        configured_questions_json: Optional[str] = None,
        is_reviewed: bool = False,
    ) -> JobRequisition:
        jd_hash = JobRepository.compute_hash(role_title, job_description)
        existing = JobRepository.get_by_hash(db, jd_hash)
        if existing:
            if blueprint_json is not None:
                existing.blueprint_json = blueprint_json
            if configured_questions_json is not None:
                existing.configured_questions_json = configured_questions_json
            existing.is_reviewed = is_reviewed
            db.commit()
            db.refresh(existing)
            return existing

        job = JobRequisition(
            jd_hash=jd_hash,
            role_title=role_title.strip(),
            job_description=job_description.strip(),
            blueprint_json=blueprint_json,
            configured_questions_json=configured_questions_json,
            is_reviewed=is_reviewed,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_questions(
        db: Session,
        job: JobRequisition,
        configured_questions_json: str,
        is_reviewed: bool = True,
    ) -> JobRequisition:
        job.configured_questions_json = configured_questions_json
        job.is_reviewed = is_reviewed
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def save(db: Session, job: JobRequisition) -> JobRequisition:
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def list_recent(db: Session, limit: int = 20) -> List[JobRequisition]:
        return (
            db.query(JobRequisition)
            .order_by(JobRequisition.created_at.desc())
            .limit(limit)
            .all()
        )
