"""
CareerLens AI - Scoring Domain
Calibrated Expected Quality scoring, multi-dimensional evaluation, and candidate ranking.
"""

from app.domain.scoring.calibrated_scorer import (
    calculate_dimension_score,
    calculate_high_hits_penalty,
    resolve_decision,
    CalibratedScorer,
    calibrated_scorer,
)

__all__ = [
    "calculate_dimension_score",
    "calculate_high_hits_penalty",
    "resolve_decision",
    "CalibratedScorer",
    "calibrated_scorer",
]
