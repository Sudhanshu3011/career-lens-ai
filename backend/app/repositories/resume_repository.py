"""
CareerLens AI - Resume Repository
Encapsulates database operations for ParsedResume entities, including PDF byte hash deduplication.
"""

from __future__ import annotations

import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.db.parsed_resume import ParsedResume


class ResumeRepository:
    """Repository layer managing ParsedResume persistence and SHA-256 byte deduplication."""

    @staticmethod
    def compute_file_hash(file_bytes: bytes) -> str:
        """Computes deterministic SHA-256 hash over raw PDF file bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def get_by_id(db: Session, resume_id: str) -> Optional[ParsedResume]:
        return db.query(ParsedResume).filter(ParsedResume.id == resume_id).first()

    @staticmethod
    def get_by_hash(db: Session, file_hash: str) -> Optional[ParsedResume]:
        return db.query(ParsedResume).filter(ParsedResume.file_hash == file_hash).first()

    @staticmethod
    def get_by_ids(db: Session, resume_ids: List[str]) -> List[ParsedResume]:
        return db.query(ParsedResume).filter(ParsedResume.id.in_(resume_ids)).all()

    @staticmethod
    def create(
        db: Session,
        file_hash: str,
        filename: str,
        file_size_bytes: int,
        status: str = "queued",
        raw_text: str = "",
        portfolio_links_json: Optional[str] = None,
        parsed_sections_json: Optional[str] = None,
    ) -> ParsedResume:
        existing = ResumeRepository.get_by_hash(db, file_hash)
        if existing:
            if parsed_sections_json is not None:
                existing.parsed_sections_json = parsed_sections_json
            if raw_text:
                existing.raw_text = raw_text
            if status:
                existing.status = status
            db.commit()
            db.refresh(existing)
            return existing

        resume = ParsedResume(
            file_hash=file_hash,
            filename=filename,
            file_size_bytes=file_size_bytes,
            status=status,
            raw_text=raw_text,
            portfolio_links_json=portfolio_links_json,
            parsed_sections_json=parsed_sections_json,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def update_completed(
        db: Session,
        resume: ParsedResume,
        parsed_sections_json: str,
        raw_text: Optional[str] = None,
        portfolio_links_json: Optional[str] = None,
    ) -> ParsedResume:
        resume.status = "completed"
        resume.parsed_sections_json = parsed_sections_json
        if raw_text is not None:
            resume.raw_text = raw_text
        if portfolio_links_json is not None:
            resume.portfolio_links_json = portfolio_links_json
        resume.error_message = None
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def update_failed(
        db: Session,
        resume: ParsedResume,
        error_message: str,
    ) -> ParsedResume:
        resume.status = "failed"
        resume.error_message = error_message
        resume.parsed_sections_json = None
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def save(db: Session, resume: ParsedResume) -> ParsedResume:
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def list_queued(db: Session) -> List[ParsedResume]:
        return (
            db.query(ParsedResume)
            .filter(ParsedResume.status == "queued")
            .order_by(ParsedResume.created_at.asc())
            .all()
        )
