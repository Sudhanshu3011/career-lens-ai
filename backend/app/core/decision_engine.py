"""
CareerLens AI - Calibrated Laya Decision Engine (Facade)

Backward-compatible facade delegating to modular domain & infrastructure components:
- Seniority classification: app.domain.seniority.classifier
- Candidate evaluation & ML inference: app.domain.scoring.candidate_evaluator
- Calibrated scoring & penalties: app.domain.scoring.calibrated_scorer
- Laya model client: app.infrastructure.ml.laya_client
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.core.logger import get_logger
from app.domain.scoring.calibrated_scorer import (
    calculate_dimension_score,
    calculate_high_hits_penalty,
    resolve_decision,
)
from app.domain.scoring.candidate_evaluator import candidate_evaluator
from app.domain.seniority.classifier import (
    ROLE_WEIGHTS,
    SENIORITY_LABELS,
    seniority_classifier,
)
from app.infrastructure.ml.laya_client import laya_client

logger = get_logger(__name__)

# Re-export key constants for backward compatibility
__all__ = [
    "ROLE_WEIGHTS",
    "SENIORITY_LABELS",
    "LayaDecisionEngine",
    "decision_engine",
    "calculate_dimension_score",
    "calculate_high_hits_penalty",
    "resolve_decision",
]


class LayaDecisionEngine:
    """
    Facade maintaining full backward compatibility with legacy calls while
    routing operations to specialized Clean Architecture domain services.
    """

    _instance: Optional[LayaDecisionEngine] = None

    @classmethod
    def get_instance(cls) -> LayaDecisionEngine:
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def is_available(self) -> bool:
        """Indicates if Laya model router is loaded and ready."""
        return laya_client.is_available

    @property
    def router(self) -> Any:
        """Direct handle to underlying Laya Router."""
        return laya_client.router

    def classify_jd_seniority(
        self,
        job_description: str,
        job_role: str = "",
    ) -> Dict[str, Any]:
        """Classifies target Job Description seniority tier and returns dynamic ROLE_WEIGHTS."""
        return seniority_classifier.classify_jd_seniority(
            job_description=job_description,
            job_role=job_role,
            laya_router=laya_client.router,
        )

    def classify_candidate_seniority(
        self,
        experience_text: str = "",
        summary_text: str = "",
        education_text: str = "",
    ) -> Dict[str, Any]:
        """Assesses candidate career seniority level from resume text and calendar spans."""
        return seniority_classifier.classify_candidate_seniority(
            experience_text=experience_text,
            summary_text=summary_text,
            education_text=education_text,
            laya_router=laya_client.router,
        )

    def evaluate_resume_match(
        self,
        candidate_skills: Dict[str, Any],
        experience_text: str,
        job_description: str,
        education_text: str = "",
        job_role: str = "",
        technical_overlap: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes calibrated multi-dimensional match evaluation:
        1. Classifies JD seniority & activates weights.
        2. Classifies candidate career level.
        3. Formulates anchored prompt & 5 parameter questions.
        4. Runs Laya inference with transparent telemetry.
        5. Computes calibrated score & high-hits penalty.
        """
        return candidate_evaluator.evaluate(
            candidate_skills=candidate_skills,
            experience_text=experience_text,
            job_description=job_description,
            education_text=education_text,
            job_role=job_role,
            technical_overlap=technical_overlap,
        )

    def evaluate_resume(
        self,
        candidate_skills: Dict[str, Any],
        experience_text: str,
        job_description: str,
        education_text: str = "",
        job_role: str = "",
        technical_overlap: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Alias for evaluate_resume_match."""
        return self.evaluate_resume_match(
            candidate_skills=candidate_skills,
            experience_text=experience_text,
            job_description=job_description,
            education_text=education_text,
            job_role=job_role,
            technical_overlap=technical_overlap,
        )

    @staticmethod
    def _calculate_high_hits_penalty(high_hits: int) -> float:
        """Penalty deduction helper for backward compatibility."""
        return calculate_high_hits_penalty(high_hits)

    @staticmethod
    def _resolve_decision(final_prob: float, high_hits: int) -> str:
        """Decision resolution helper for backward compatibility."""
        return resolve_decision(final_prob, high_hits)


# Singleton instance
decision_engine = LayaDecisionEngine.get_instance()
