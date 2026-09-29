"""
CareerLens AI - Resume Analysis Schemas
Pydantic V2 models for resume analysis, scoring breakdowns, and evaluation feedback.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ParameterDetailSchema(BaseModel):
    p_high: float = Field(..., description="Laya probability for high match")
    p_mid: float = Field(..., description="Laya probability for mid/medium match")
    p_low: float = Field(..., description="Laya probability for low match")
    selected_prob: float = Field(
        ..., description="Selected probability: max(p_high, p_mid)"
    )
    weight: float = Field(
        ..., description="Active weight triggered by JD seniority tier"
    )
    weighted_score: float = Field(
        ..., description="Contribution score: selected_prob * weight"
    )
    is_high_hit: bool = Field(
        ..., description="Whether candidate hit high as dominant choice"
    )
    percentage: int = Field(..., description="Display percentage (0-100)")

    model_config = ConfigDict(extra="allow")


class DecisionBreakdownSchema(BaseModel):
    technical_requirements: int = Field(
        ..., description="Percentage match for technical skills and tools"
    )
    experience_requirements: int = Field(
        ..., description="Percentage match for role experience and seniority"
    )
    domain_alignment: int = Field(
        ..., description="Percentage alignment with industry/problem domain"
    )
    education_alignment: int = Field(
        70, description="Percentage alignment for academic and education credentials"
    )
    evidence_strength: int = Field(
        ..., description="Percentage score for concrete proof and metrics in resume"
    )

    model_config = ConfigDict(extra="allow")


class ScoreEvaluationSchema(BaseModel):
    final_score: Optional[float] = Field(
        default=None, description="Calibrated unified score on 0 to 10 scale"
    )
    fit_score: Optional[float] = Field(
        default=None, description="Calibrated fit percentage on 0 to 100 scale"
    )
    overall_decision: str = Field(
        "Moderate match",
        description="Decision verdict: Strong match, Moderate match, etc.",
    )
    seniority_tier: str = Field(
        "mid_level", description="JD seniority tier: beginner, mid_level, senior"
    )
    seniority_label: str = Field("Mid-Level", description="Descriptive seniority title")
    role_weights: Dict[str, float] = Field(
        default_factory=dict, description="Active parameter weights triggered by JD"
    )
    raw_weighted_probability: float = Field(
        0.0, description="Raw weighted sum before penalty"
    )
    high_hits_count: int = Field(
        0, description="Number of dimensions where high flag was hit (0-5)"
    )
    penalty_applied: float = Field(
        0.0, description="Penalty deducted for least high hits: max(0, (3-H)*0.02)"
    )
    total_weighted_probability: float = Field(
        0.0, description="Final penalized weighted probability"
    )
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
