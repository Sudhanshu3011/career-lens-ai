"""
CareerLens AI - TypeSafe Decision & Scoring Domain Models
Hard gates, seniority gaps, composite weighting, confidence routing, and review flags.
"""

from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, Field


class HardRequirementGate(BaseModel):
    """Result of evaluating a mandatory qualification gate."""

    requirement_name: str
    passed: bool
    probability: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""


class SeniorityAssessment(BaseModel):
    """Continuous seniority comparison and gap analysis."""

    jd_seniority_score: float = Field(..., ge=0.0, le=6.0)
    jd_seniority_label: str
    candidate_seniority_score: float = Field(..., ge=0.0, le=6.0)
    candidate_seniority_label: str
    seniority_gap: float = Field(..., description="candidate_score - jd_score")
    alignment_label: str = Field(..., description="ALIGNED, GAP, or EXCEEDS")
    alignment_note: str = ""
    confidence: float = 0.0


class CompositeScore(BaseModel):
    """Deterministic weighted multi-dimensional score."""

    seniority_score: float = Field(default=0.0, ge=0.0, le=100.0)
    technical_score: float = Field(default=0.0, ge=0.0, le=100.0)
    experience_score: float = Field(default=0.0, ge=0.0, le=100.0)
    domain_score: float = Field(default=0.0, ge=0.0, le=100.0)
    requirements_score: float = Field(default=0.0, ge=0.0, le=100.0)
    education_score: float = Field(default=0.0, ge=0.0, le=100.0)
    final_fit_score: float = Field(default=0.0, ge=0.0, le=100.0)
    weights: Dict[str, float] = Field(default_factory=dict)


class DecisionState(BaseModel):
    """Complete aggregated evaluation outcome for a candidate."""

    candidate_id: str
    candidate_name: str
    overall_decision: str = Field(..., description="SELECT, BORDERLINE, or REJECT")
    hard_gates_passed: bool = Field(
        default=True, description="Whether all mandatory gates passed"
    )
    failed_hard_gates: List[str] = Field(default_factory=list)

    seniority: SeniorityAssessment
    composite: CompositeScore
    gate_evaluations: List[HardRequirementGate] = Field(default_factory=list)
    review_flags: List[str] = Field(default_factory=list)
    confidence_tier: str = Field(
        default="AUTOMATIC", description="AUTOMATIC, UNCERTAIN, or NEEDS_REVIEW"
    )
    decision_reason: str = ""
