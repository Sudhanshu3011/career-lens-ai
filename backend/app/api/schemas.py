"""
CareerLens AI - API Schemas & Data Transfer Objects (DTOs)

Centralized Pydantic V2 models for request validation and response serialization
across all API endpoints and service layers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Decision & Scoring Schemas
# ---------------------------------------------------------------------------

class ParameterDetailSchema(BaseModel):
    p_high: float = Field(..., description="Laya probability for high match")
    p_mid: float = Field(..., description="Laya probability for mid/medium match")
    p_low: float = Field(..., description="Laya probability for low match")
    selected_prob: float = Field(..., description="Selected probability: max(p_high, p_mid)")
    weight: float = Field(..., description="Active weight triggered by JD seniority tier")
    weighted_score: float = Field(..., description="Contribution score: selected_prob * weight")
    is_high_hit: bool = Field(..., description="Whether candidate hit high as dominant choice")
    percentage: int = Field(..., description="Display percentage (0-100)")

    model_config = ConfigDict(extra="allow")


class DecisionBreakdownSchema(BaseModel):
    technical_requirements: int = Field(..., description="Percentage match for technical skills and tools")
    experience_requirements: int = Field(..., description="Percentage match for role experience and seniority")
    domain_alignment: int = Field(..., description="Percentage alignment with industry/problem domain")
    education_alignment: int = Field(70, description="Percentage alignment for academic and education credentials")
    evidence_strength: int = Field(..., description="Percentage score for concrete proof and metrics in resume")

    model_config = ConfigDict(extra="allow")


class ScoreEvaluationSchema(BaseModel):
    final_score: Optional[float] = Field(default=None, description="Calibrated unified score on 0 to 10 scale")
    fit_score: Optional[float] = Field(default=None, description="Calibrated fit percentage on 0 to 100 scale")
    overall_decision: str = Field("Moderate match", description="Decision verdict: Strong match, Moderate match, etc.")
    seniority_tier: str = Field("mid_level", description="JD seniority tier: beginner, mid_level, senior")
    seniority_label: str = Field("Mid-Level", description="Descriptive seniority title")
    role_weights: Dict[str, float] = Field(default_factory=dict, description="Active parameter weights triggered by JD")
    raw_weighted_probability: float = Field(0.0, description="Raw weighted sum before penalty")
    high_hits_count: int = Field(0, description="Number of dimensions where high flag was hit (0-5)")
    penalty_applied: float = Field(0.0, description="Penalty deducted for least high hits: max(0, (3-H)*0.02)")
    total_weighted_probability: float = Field(0.0, description="Final penalized weighted probability")
    breakdown: Optional[Dict[str, float]] = Field(default_factory=dict)
    parameter_evaluations: Optional[Dict[str, Any]] = Field(default_factory=dict)
    technical_overlap: Optional[Dict[str, Any]] = Field(default_factory=dict)
    source: str = Field("laya_decision_engine", description="Scoring source model")

    model_config = ConfigDict(extra="allow")


class ResumeAnalysisData(BaseModel):
    parsed_resume: Dict[str, Any]
    skills_analysis: Dict[str, Any]
    decision_breakdown: Dict[str, float]
    scores: Dict[str, Any]
    feedback: List[str]
    strengths: Optional[List[str]] = Field(default_factory=list)
    growth_areas: Optional[List[str]] = Field(default_factory=list)
    actionable_steps: Optional[List[str]] = Field(default_factory=list)
    elevation_roadmap: Optional[Dict[str, str]] = Field(default_factory=dict)
    seniority_tier: Optional[str] = "mid_level"
    seniority_label: Optional[str] = "Mid-Level"
    role_weights: Optional[Dict[str, float]] = None
    high_hits_count: Optional[int] = 0
    recommended_jobs: Optional[List[Any]] = Field(default_factory=list)
    best_job_recommendation: Optional[Any] = None

    model_config = ConfigDict(extra="allow")


class ResumeAnalysisResponse(BaseModel):
    success: bool = True
    data: ResumeAnalysisData


# ---------------------------------------------------------------------------
# Enterprise Bulk Screener Schemas
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Session Showcase Candidate Screening Schemas
# ---------------------------------------------------------------------------

class CandidateScreeningItem(BaseModel):
    id: str
    name: str
    title: str
    fit_score: int
    decision: str
    rank: int
    is_top_3: bool
    is_top_5: bool
    skills: List[str]
    missing_skills: List[str]
    explanation: str

    model_config = ConfigDict(extra="allow")


class CandidateScreeningInput(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    title: Optional[str] = ""
    skills: List[str] = Field(default_factory=list)
    experience_text: Optional[str] = ""
    education: Optional[str] = ""
    summary: Optional[str] = ""

    model_config = ConfigDict(extra="allow")


class BatchScreeningRequest(BaseModel):
    job_description: str
    candidates: List[CandidateScreeningInput] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class CandidateScreeningResponse(BaseModel):
    success: bool = True
    total_candidates: int
    top_3_count: int
    top_5_count: int
    selected_count: int
    candidates: List[CandidateScreeningItem]


class QuickApplySchema(BaseModel):
    verdict: str = Field(..., description="Recommendation verdict: Strong Apply, Good Match, Reach Role, Low Fit")
    fit_score: int = Field(..., description="Calculated fit score percentage (0-100)")
    confidence: int = Field(85, description="Confidence percentage in verdict (0-100)")
    highlights: List[str] = Field(default_factory=list, description="Key alignment factors")

    model_config = ConfigDict(extra="allow")


class QuickApplyRequest(BaseModel):
    candidate_skills: Dict[str, List[str]] = Field(
        ...,
        description="Candidate skills categorized into technical_skills, tools_and_platforms, domains",
    )
    job_title: str = Field(..., description="Target job title")
    job_company: Optional[str] = Field("", description="Company name")
    job_location: Optional[str] = Field("", description="Location")
    job_description: Optional[str] = Field("", description="Job description or snippet")


class QuickApplyResponse(BaseModel):
    success: bool = True
    job_title: str
    decision: QuickApplySchema


ShouldIApplySchema = QuickApplySchema
ShouldIApplyRequest = QuickApplyRequest
ShouldIApplyResponse = QuickApplyResponse


# ---------------------------------------------------------------------------
# Transparent Job Requirements Preview Schemas
# ---------------------------------------------------------------------------

class DetectedRequirementItem(BaseModel):
    name: str = Field(..., description="Requirement or skill name")
    category: str = Field("skill", description="Category: skill, tool, framework, domain")
    is_hard_requirement: bool = Field(False, description="Whether this is a mandatory gate (dealbreaker)")
    target_years: Optional[float] = Field(None, description="Explicit required experience in years if detected")
    description: Optional[str] = Field("", description="Requirement context or explanation")
    suggested_gate_question: Optional[str] = Field(None, description="Preview of Noul gate question")
    suggested_direct_question: Optional[str] = Field(None, description="Preview of Noul direct evidence question")
    suggested_strength_question: Optional[str] = Field(None, description="Preview of Score 0-5 strength question")

    model_config = ConfigDict(extra="allow")


class ApprovedRequirementInput(BaseModel):
    name: str = Field(..., description="Requirement name")
    is_hard_requirement: bool = Field(False, description="True if mandatory gate, False if standard evaluated skill")
    category: Optional[str] = Field("skill", description="Category")


class JDPreviewRequest(BaseModel):
    job_role: str = Field(..., min_length=2, description="Target Job Role title, e.g. Senior Backend Engineer")
    job_description: str = Field(..., min_length=20, description="Full job description requirements text")
    pipeline: str = Field("typesafe", description="Target pipeline: 'typesafe' or 'laya_local'")


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

