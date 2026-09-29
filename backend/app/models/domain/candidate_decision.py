from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    competency_depth: float = Field(default=0.0, description="Score contribution from core domain competencies (0-100)")
    seniority_fit: float = Field(default=0.0, description="Score contribution from seniority calibration (0-100)")
    experience_duration: float = Field(default=0.0, description="Score contribution from verified tenure timeline (0-100)")
    domain_alignment: float = Field(default=0.0, description="Score contribution from domain category (0-100)")
    evidence_quality: float = Field(default=0.0, description="Score contribution from quantifiable evidence (0-100)")
    education_credentials: float = Field(default=0.0, description="Score contribution from education and degrees (0-100)")
    raw_weighted_total: float = Field(default=0.0, description="Uncapped composite weighted score (0-100)")


class GateResult(BaseModel):
    name: str = Field(description="Name or label of the hard requirement / dealbreaker")
    question: str = Field(description="The verification assertion checked")
    passed: bool = Field(description="Whether the candidate met this mandatory requirement")
    probability: float = Field(description="Confidence/probability P(assertion = True)")


class CandidateVerdict(BaseModel):
    candidate_name: str
    fit_score: float = Field(description="Final normalized fit score (0.0 - 100.0)")
    overall_decision: str = Field(description="'ADVANCE', 'HOLD', or 'REJECT'")
    domain_classification: str = Field(
        default="direct_domain_match",
        description="'direct_domain_match', 'adjacent_domain_transfer', or 'unrelated_background'",
    )
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    failed_hard_gates: List[GateResult] = Field(default_factory=list)
    passed_hard_gates: List[GateResult] = Field(default_factory=list)
    veto_reason: Optional[str] = Field(
        default=None,
        description="Reason for early rejection or score capping (e.g., 'domain_competency_gate_failed', 'mandatory_dealbreaker_failed')",
    )
    summary_feedback: str = Field(default="", description="Executive recruiting rationale")
    engine_used: str = Field(default="jev", description="Evaluation engine used ('jev' or 'laya')")
