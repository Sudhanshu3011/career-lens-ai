"""
CareerLens AI - Universal Domain Models Package
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
    # Universal Resume Sections
    "EducationItem",
    "ResumeParsedSections",
    "WorkExperienceItem",
    # Dynamic Blueprints
    "AscendingAssessmentBlueprint",
    "BackgroundClassificationBlueprint",
    "EvaluationQuestionsBlueprint",
    "MandatoryDealbreakerBlueprint",
    # Candidate Verdict & Decision
    "CandidateVerdict",
    "GateResult",
    "ScoreBreakdown",
]
