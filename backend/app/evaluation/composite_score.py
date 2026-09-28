"""
CareerLens AI - Composite Score & Decision Aggregator
Calculates deterministic weighted multi-dimensional score and applies hard gate rules.
"""

from __future__ import annotations

from typing import Dict, List
from app.models.decision import DecisionState, CompositeScore, HardRequirementGate, SeniorityAssessment
from app.models.evidence import EvidenceAssessment
from app.evaluation.seniority_evaluator import compute_seniority_fit_percentage
from app.jev.confidence import evaluate_batch_confidence


# Standardized, transparent dimension weights (sums to 1.0)
DEFAULT_DIMENSION_WEIGHTS: Dict[str, float] = {
    "technical": 0.25,
    "seniority": 0.20,
    "experience": 0.20,
    "domain": 0.15,
    "requirements": 0.15,
    "education": 0.05,
}


def calculate_composite_decision(
    candidate_id: str,
    candidate_name: str,
    seniority: SeniorityAssessment,
    assessments: List[EvidenceAssessment],
    hard_gates: List[HardRequirementGate],
    all_hard_gates_passed: bool,
    technical_overlap_pct: float,
    domain_overlap_pct: float,
    has_education: bool,
    weights: Dict[str, float] = DEFAULT_DIMENSION_WEIGHTS,
) -> DecisionState:
    """
    Combines atomic dimension judgments and applies hard requirement gates in pure Python:
    1. Aggregates dimension component scores (0-100).
    2. Applies configurable weights.
    3. Enforces hard requirement gate veto.
    4. Evaluates confidence tier and flags.
    """
    # 1. Dimension component scores (0.0 to 100.0)
    sen_fit = compute_seniority_fit_percentage(seniority.seniority_gap)
    tech_fit = max(10.0, min(100.0, technical_overlap_pct))

    # Experience fit based on direct evidence and seniority alignment
    exp_evidence_avg = (
        sum(a.direct_evidence_probability for a in assessments) / len(assessments)
        if assessments else 0.5
    )
    exp_fit = round(0.60 * sen_fit + 0.40 * (exp_evidence_avg * 100.0), 1)

    dom_fit = max(20.0, min(100.0, domain_overlap_pct))
    
    req_evidence_avg = (
        sum(a.satisfied_probability for a in assessments) / len(assessments)
        if assessments else 0.5
    )
    req_fit = round(req_evidence_avg * 100.0, 1)

    edu_fit = 90.0 if has_education else 40.0

    # 2. Composite weighted calculation
    w = weights
    final_score = (
        w["technical"] * tech_fit
        + w["seniority"] * sen_fit
        + w["experience"] * exp_fit
        + w["domain"] * dom_fit
        + w["requirements"] * req_fit
        + w["education"] * edu_fit
    )
    final_score = round(max(0.0, min(100.0, final_score)), 1)

    composite = CompositeScore(
        seniority_score=sen_fit,
        technical_score=tech_fit,
        experience_score=exp_fit,
        domain_score=dom_fit,
        requirements_score=req_fit,
        education_score=edu_fit,
        final_fit_score=final_score,
        weights=w,
    )

    # 3. Hard requirement gates enforcement
    review_flags: List[str] = []
    failed_gates = [g.requirement_name for g in hard_gates if not g.passed]

    # 4. Confidence evaluation
    confidences = [seniority.confidence] + [a.confidence for a in assessments]
    mean_conf, conf_tier, conf_flags = evaluate_batch_confidence(confidences)
    review_flags.extend(conf_flags)

    # 5. Resolve Overall Decision
    if not all_hard_gates_passed:
        overall_decision = "REJECT"
        review_flags.append(f"Hard gate failure: unmet mandatory requirement(s): {', '.join(failed_gates)}")
        reason = (
            f"Candidate achieved {final_score}% overall fit but failed mandatory requirement(s): "
            f"{', '.join(failed_gates)}. {seniority.alignment_note}"
        )
    elif final_score >= 75.0 and mean_conf >= 0.65:
        overall_decision = "SELECT"
        reason = (
            f"Strong candidate alignment ({final_score}%). All {len(hard_gates)} hard requirements verified. "
            f"{seniority.alignment_note}"
        )
    elif final_score >= 50.0:
        overall_decision = "BORDERLINE"
        reason = (
            f"Moderate candidate alignment ({final_score}%). Requirements partially satisfied. "
            f"{seniority.alignment_note}"
        )
    else:
        overall_decision = "REJECT"
        reason = (
            f"Insufficient technical/seniority alignment ({final_score}%). "
            f"{seniority.alignment_note}"
        )

    return DecisionState(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        overall_decision=overall_decision,
        hard_gates_passed=all_hard_gates_passed,
        failed_hard_gates=failed_gates,
        seniority=seniority,
        composite=composite,
        gate_evaluations=hard_gates,
        review_flags=review_flags,
        confidence_tier=conf_tier,
        decision_reason=reason,
    )
