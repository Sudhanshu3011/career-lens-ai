"""
CareerLens AI - Pydantic V2 Schemas Package
"""

from app.schemas.analysis import (
    DecisionBreakdownSchema,
    ParameterDetailSchema,
    ResumeAnalysisData,
    ResumeAnalysisResponse,
    ScoreEvaluationSchema,
)
from app.schemas.enterprise import (
    ApprovedRequirementInput,
    DetectedRequirementItem,
    EnterpriseBulkScreenResponse,
    EnterpriseCandidateSchema,
    JDPreviewRequest,
    JDPreviewResponse,
)
from app.schemas.session import (
    BatchScreeningRequest,
    CandidateScreeningInput,
    CandidateScreeningItem,
    CandidateScreeningResponse,
    SessionSummarySchema,
)

__all__ = [
    # Analysis
    "ParameterDetailSchema",
    "DecisionBreakdownSchema",
    "ScoreEvaluationSchema",
    "ResumeAnalysisData",
    "ResumeAnalysisResponse",
    # Enterprise
    "EnterpriseCandidateSchema",
    "EnterpriseBulkScreenResponse",
    "DetectedRequirementItem",
    "ApprovedRequirementInput",
    "JDPreviewRequest",
    "JDPreviewResponse",
    # Session
    "CandidateScreeningItem",
    "CandidateScreeningInput",
    "BatchScreeningRequest",
    "CandidateScreeningResponse",
    "SessionSummarySchema",
]
