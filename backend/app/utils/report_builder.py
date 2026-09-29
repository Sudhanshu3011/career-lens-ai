"""
CareerLens AI - Report Builder
Formats decomposed TypeSafe assessments into API response contracts for the frontend.
"""

from __future__ import annotations

from typing import Any, Dict
from app.models.domain.job import JobProfile
from app.models.domain.candidate import CandidateProfile
from app.models.domain.decision import DecisionState


def build_candidate_enterprise_record(
    idx: int,
    filename: str,
    candidate: CandidateProfile,
    job: JobProfile,
    decision_state: DecisionState,
    technical_overlap: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Constructs backward-compatible and enriched enterprise candidate record
    compatible with frontend CandidateCard and EnterpriseBulkScreener components.
    """
    comp = decision_state.composite
    sen = decision_state.seniority

    return {
        "candidate_id": decision_state.candidate_id or f"cand-{idx + 1}",
        "name": candidate.candidate_name,
        "filename": filename,
        "fit_score": comp.final_fit_score,
        "raw_score": round(comp.final_fit_score / 10.0, 1),
        "decision": decision_state.overall_decision,
        "seniority_tier": sen.candidate_seniority_label.lower()
        .replace(" ", "_")
        .replace("/", "_"),
        "seniority_label": sen.candidate_seniority_label,
        "target_seniority_tier": sen.jd_seniority_label.lower()
        .replace(" ", "_")
        .replace("/", "_"),
        "target_seniority_label": sen.jd_seniority_label,
        "candidate_seniority_tier": sen.candidate_seniority_label.lower()
        .replace(" ", "_")
        .replace("/", "_"),
        "candidate_seniority_label": sen.candidate_seniority_label,
        "seniority_alignment": sen.alignment_label,
        "role_weights": comp.weights,
        "high_hits_count": sum(1 for g in decision_state.gate_evaluations if g.passed),
        "raw_weighted_probability": round(comp.final_fit_score / 100.0, 4),
        "penalty_applied": 0.0 if decision_state.hard_gates_passed else 0.15,
        "total_weighted_probability": round(comp.final_fit_score / 100.0, 4),
        "breakdown": {
            "technical_requirements": round(comp.technical_score, 1),
            "experience_requirements": round(comp.experience_score, 1),
            "domain_alignment": round(comp.domain_score, 1),
            "education_alignment": round(comp.education_score, 1),
            "evidence_strength": round(comp.requirements_score, 1),
        },
        "parameter_evaluations": {},
        "skills": candidate.technical_skills,
        "tools": candidate.tools,
        "domains": candidate.domains,
        "decision_reason": decision_state.decision_reason,
        "technical_overlap": technical_overlap,
        "inspection": {
            "summary": candidate.summary_text,
            "experience": candidate.experience_text,
            "education": candidate.education_text,
            "skills": ", ".join(candidate.technical_skills),
            "contact_info": {
                "email": candidate.email,
                "phone": candidate.phone,
                "all_urls": candidate.hyperlinks,
            },
        },
        # TypeSafe System One Enriched Fields
        "typesafe_telemetry": {
            "hard_gates_passed": decision_state.hard_gates_passed,
            "failed_hard_gates": decision_state.failed_hard_gates,
            "seniority_gap": sen.seniority_gap,
            "confidence_tier": decision_state.confidence_tier,
            "review_flags": decision_state.review_flags,
            "gates_detail": [g.model_dump() for g in decision_state.gate_evaluations],
        },
    }


class ReportBuilder:
    """Builder class for serializing evaluation reports."""

    build_candidate_enterprise_record = staticmethod(build_candidate_enterprise_record)
