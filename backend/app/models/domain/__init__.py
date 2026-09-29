"""
CareerLens AI - Domain Models Package
"""

from app.models.domain.candidate import CandidateProfile, ResumeBlock
from app.models.domain.decision import (
    CompositeScore,
    DecisionState,
    HardRequirementGate,
    SeniorityAssessment,
)
from app.models.domain.evidence import Evidence, EvidenceAssessment
from app.models.domain.job import JobProfile, RequirementItem

__all__ = [
    "CandidateProfile",
    "ResumeBlock",
    "CompositeScore",
    "DecisionState",
    "HardRequirementGate",
    "SeniorityAssessment",
    "Evidence",
    "EvidenceAssessment",
    "JobProfile",
    "RequirementItem",
]
