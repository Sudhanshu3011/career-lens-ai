"""
CareerLens AI - Candidate Scorer (Backward-Compatibility Shim)

Re-exports scoring functions from app.domain.scoring.candidate_scorer.
"""

from __future__ import annotations

from app.domain.scoring.candidate_scorer import (
    score_resume_against_jd,
    score_resume_against_jd_zero_llm,
)

__all__ = [
    "score_resume_against_jd",
    "score_resume_against_jd_zero_llm",
]
