"""
CareerLens AI - TypeSafe Domain Data Models
"""

from app.models.job_profile import JobProfile, RequirementItem
from app.models.candidate_profile import CandidateProfile, ResumeBlock
from app.models.evidence import Evidence, EvidenceAssessment
from app.models.decision import DecisionState, CompositeScore, HardRequirementGate, SeniorityAssessment

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
]
