"""
CareerLens AI - Candidate Evaluation Repository
Encapsulates database operations for CandidateEvaluation records.
"""

from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.db.candidate_evaluation import CandidateEvaluation


class EvaluationRepository:
    """Repository layer managing CandidateEvaluation persistence and queries."""

    @staticmethod
    def get_by_id(db: Session, eval_id: str) -> Optional[CandidateEvaluation]:
        return db.query(CandidateEvaluation).filter(CandidateEvaluation.id == eval_id).first()

    @staticmethod
    def get_by_job_and_resume(
        db: Session, job_id: str, resume_id: str
    ) -> Optional[CandidateEvaluation]:
        return (
            db.query(CandidateEvaluation)
            .filter(
                CandidateEvaluation.job_id == job_id,
                CandidateEvaluation.resume_id == resume_id,
            )
            .first()
        )

    @staticmethod
    def list_by_job(db: Session, job_id: str) -> List[CandidateEvaluation]:
        return (
            db.query(CandidateEvaluation)
            .filter(CandidateEvaluation.job_id == job_id)
            .order_by(CandidateEvaluation.fit_score.desc())
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        job_id: str,
        resume_id: str,
        candidate_name: str,
        pipeline: str = "laya",
        status: str = "pending",
        fit_score: float = 0.0,
        verdict: str = "HOLD",
        verdict_json: Optional[str] = None,
    ) -> CandidateEvaluation:
        evaluation = CandidateEvaluation(
            job_id=job_id,
            resume_id=resume_id,
            candidate_name=candidate_name,
            pipeline=pipeline,
            status=status,
            fit_score=fit_score,
            verdict=verdict,
            verdict_json=verdict_json,
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def update_completed(
        db: Session,
        evaluation: CandidateEvaluation,
        fit_score: float,
        verdict: str,
        verdict_json: str,
    ) -> CandidateEvaluation:
        evaluation.status = "completed"
        evaluation.fit_score = fit_score
        evaluation.verdict = verdict
        evaluation.verdict_json = verdict_json
        evaluation.error_message = None
        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def update_failed(
        db: Session,
        evaluation: CandidateEvaluation,
        error_message: str,
    ) -> CandidateEvaluation:
        evaluation.status = "failed"
        evaluation.error_message = error_message
        db.commit()
        db.refresh(evaluation)
        return evaluation
