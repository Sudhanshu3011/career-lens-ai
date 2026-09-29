"""
CareerLens AI - Enterprise Bulk Screener Schemas
Pydantic V2 models for enterprise bulk screening, JD requirement preview, and candidate ranking.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EnterpriseCandidateSchema(BaseModel):
    candidate_id: str
    name: str
    filename: str
    fit_score: float
    raw_score: float
    decision: str
    rank: Optional[int] = None
    is_top_3: Optional[bool] = None
    is_top_5: Optional[bool] = None
    seniority_tier: Optional[str] = "mid_level"
    seniority_label: Optional[str] = "Mid-Level"
    target_seniority_tier: Optional[str] = "senior"
    target_seniority_label: Optional[str] = "Senior / Lead"
    candidate_seniority_tier: Optional[str] = "mid_level"
    candidate_seniority_label: Optional[str] = "Mid-Level"
    seniority_alignment: Optional[str] = "ALIGNED"
    role_weights: Optional[Dict[str, float]] = None
    high_hits_count: int = 0
    raw_weighted_probability: float = 0.0
    penalty_applied: float = 0.0
    total_weighted_probability: float = 0.0
    breakdown: Dict[str, float]
    parameter_evaluations: Optional[Dict[str, Any]] = None
    skills: List[str] = []
    tools: List[str] = []
    domains: List[str] = []
    decision_reason: str = ""
    technical_overlap: Dict[str, Any] = {}
    inspection: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


class EnterpriseBulkScreenResponse(BaseModel):
    success: bool = True
    job_role: str
    seniority_tier: Optional[str] = "mid_level"
    seniority_label: Optional[str] = "Mid-Level"
    role_weights: Optional[Dict[str, float]] = None
    total_evaluated: int
    top_3_shortlisted: int
    top_5_shortlisted: int
    selected_candidates_count: int
    average_fit_score: float
    latency_seconds: float
    candidates: List[EnterpriseCandidateSchema]


class DetectedRequirementItem(BaseModel):
    name: str = Field(..., description="Requirement or skill name")
    category: str = Field(
        "skill", description="Category: skill, tool, framework, domain"
    )
    is_hard_requirement: bool = Field(
        False, description="Whether this is a mandatory gate (dealbreaker)"
    )
    target_years: Optional[float] = Field(
        None, description="Explicit required experience in years if detected"
    )
    description: Optional[str] = Field(
        "", description="Requirement context or explanation"
    )
    suggested_gate_question: Optional[str] = Field(
        None, description="Preview of Noul gate question"
    )
    suggested_direct_question: Optional[str] = Field(
        None, description="Preview of Noul direct evidence question"
    )
    suggested_strength_question: Optional[str] = Field(
        None, description="Preview of Score 0-5 strength question"
    )

    model_config = ConfigDict(extra="allow")


class ApprovedRequirementInput(BaseModel):
    name: str = Field(..., description="Requirement name")
    is_hard_requirement: bool = Field(
        False, description="True if mandatory gate, False if standard evaluated skill"
    )
    category: Optional[str] = Field("skill", description="Category")


class JDPreviewRequest(BaseModel):
    job_role: str = Field(
        ...,
        min_length=2,
        description="Target Job Role title, e.g. Senior Backend Engineer",
    )
    job_description: str = Field(
        ..., min_length=20, description="Full job description requirements text"
    )
    pipeline: str = Field(
        "typesafe", description="Target pipeline: 'typesafe' or 'laya_local'"
    )


class JDPreviewResponse(BaseModel):
    success: bool = True
    job_role: str
    seniority_score: float
    seniority_label: str
    role_family: str
    domain: str
    total_detected_skills: int
    detected_skills_by_category: Dict[str, List[str]]
    suggested_requirements: List[DetectedRequirementItem]
    preview_questions_summary: Dict[str, Any]

    model_config = ConfigDict(extra="allow")
