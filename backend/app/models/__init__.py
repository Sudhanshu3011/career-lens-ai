"""
CareerLens AI - TypeSafe Domain & Database Models
"""

from app.models.domain.job import JobProfile, RequirementItem
from app.models.domain.candidate import CandidateProfile, ResumeBlock
from app.models.domain.evidence import Evidence, EvidenceAssessment
from app.models.domain.decision import (
    DecisionState,
    CompositeScore,
    HardRequirementGate,
    SeniorityAssessment,
)
from app.models.db.session import AnalysisSession

__all__ = [
    "JobProfile",
    "RequirementItem",
    "CandidateProfile",
    "ResumeBlock",
    "Evidence",
    "EvidenceAssessment",
    "DecisionState",
    "CompositeScore",
    "HardRequirementGate",
    "SeniorityAssessment",
    "AnalysisSession",
]
