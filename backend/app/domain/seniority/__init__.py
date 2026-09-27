"""
CareerLens AI - Seniority Domain
Classification logic and criteria for job requisition and candidate career tiers.
"""

from app.domain.seniority.classifier import (
    SENIORITY_LABELS,
    ROLE_WEIGHTS,
    SeniorityClassifier,
    seniority_classifier,
)

__all__ = [
    "SENIORITY_LABELS",
    "ROLE_WEIGHTS",
    "SeniorityClassifier",
    "seniority_classifier",
]
