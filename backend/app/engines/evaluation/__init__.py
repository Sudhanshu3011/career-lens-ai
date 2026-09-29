"""
CareerLens AI - Deterministic Evaluation and Aggregation Package
"""

from app.engines.evaluation.seniority_evaluator import (
    evaluate_seniority_gap,
    compute_seniority_fit_percentage,
)
from app.engines.evaluation.requirement_matcher import evaluate_candidate_requirements
from app.engines.evaluation.composite_score import (
    calculate_composite_decision,
    DEFAULT_DIMENSION_WEIGHTS,
)

__all__ = [
    "evaluate_seniority_gap",
    "compute_seniority_fit_percentage",
    "evaluate_candidate_requirements",
    "calculate_composite_decision",
    "DEFAULT_DIMENSION_WEIGHTS",
]
