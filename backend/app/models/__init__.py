"""
CareerLens AI - Universal Models Package
"""

from app.models.domain.candidate_decision import (
    CandidateVerdict,
    GateResult,
    ScoreBreakdown,
)
from app.models.domain.dynamic_blueprint import (
    AscendingAssessmentBlueprint,
    BackgroundClassificationBlueprint,
    EvaluationQuestionsBlueprint,
    MandatoryDealbreakerBlueprint,
)
from app.models.domain.resume_sections import (
    EducationItem,
    ResumeParsedSections,
    WorkExperienceItem,
)

__all__ = [
    # Universal Domain Models
    "EducationItem",
    "ResumeParsedSections",
    "WorkExperienceItem",
    "AscendingAssessmentBlueprint",
    "BackgroundClassificationBlueprint",
    "EvaluationQuestionsBlueprint",
    "MandatoryDealbreakerBlueprint",
    "CandidateVerdict",
    "GateResult",
    "ScoreBreakdown",
]
