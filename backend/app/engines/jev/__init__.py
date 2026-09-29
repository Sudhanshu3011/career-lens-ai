"""
CareerLens AI - TypeSafe Jev System One Integration
Powered by official typesafe-sdk.
"""

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
from app.engines.jev.client import JevClient, jev_client
from app.engines.jev.rubric import RESUME_RUBRIC_V1, seniority_score_to_label
from app.engines.jev.questions import (
    build_jd_questions,
    build_candidate_seniority_question,
    build_requirement_questions,
    build_section_classifier_question,
)
from app.engines.jev.confidence import (
    classify_confidence_tier,
    evaluate_batch_confidence,
)

__all__ = [
    "Choice",
    "Noul",
    "Score",
    "TypeSafeClient",
    "JevClient",
    "jev_client",
    "RESUME_RUBRIC_V1",
    "seniority_score_to_label",
    "build_jd_questions",
    "build_candidate_seniority_question",
    "build_requirement_questions",
    "build_section_classifier_question",
    "classify_confidence_tier",
    "evaluate_batch_confidence",
]
