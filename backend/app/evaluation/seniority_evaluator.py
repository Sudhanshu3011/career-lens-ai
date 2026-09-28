"""
CareerLens AI - Continuous Seniority Evaluator
Computes ordered continuous gap (Candidate Score - JD Score) and alignment notes.
"""

from __future__ import annotations

from typing import Dict
from app.models.decision import SeniorityAssessment
from app.jev.rubric import seniority_score_to_label


def evaluate_seniority_gap(
    jd_score: float,
    candidate_score: float,
    confidence: float = 0.80,
) -> SeniorityAssessment:
    """
    Evaluates continuous gap between candidate career seniority and target requisition:
    gap = candidate_score - jd_score (e.g. 2.4 - 3.2 = -0.8)
    """
    gap = round(candidate_score - jd_score, 2)
    jd_label = seniority_score_to_label(jd_score)
    cand_label = seniority_score_to_label(candidate_score)

    if abs(gap) <= 0.8:
        alignment_label = "ALIGNED"
        alignment_note = f"Candidate seniority ({cand_label}, {candidate_score:.1f}) closely aligns with target role ({jd_label}, {jd_score:.1f})."
    elif gap < -0.8:
        alignment_label = "GAP"
        alignment_note = f"Seniority gap: Candidate is {cand_label} ({candidate_score:.1f}) applying for a {jd_label} ({jd_score:.1f}) position."
    else:
        alignment_label = "EXCEEDS"
        alignment_note = f"Candidate seniority ({cand_label}, {candidate_score:.1f}) exceeds {jd_label} ({jd_score:.1f}) requisition requirements."

    return SeniorityAssessment(
        jd_seniority_score=jd_score,
        jd_seniority_label=jd_label,
        candidate_seniority_score=candidate_score,
        candidate_seniority_label=cand_label,
        seniority_gap=gap,
        alignment_label=alignment_label,
        alignment_note=alignment_note,
        confidence=confidence,
    )


def compute_seniority_fit_percentage(gap: float) -> float:
    """
    Converts seniority gap into a 0-100% component score for composite aggregation.
    - gap = 0.0 -> 100%
    - gap = -1.0 -> 75%
    - gap = -2.0 -> 45%
    - gap = -3.0+ -> 20%
    - gap = +1.0 (overqualified) -> 90%
    """
    if gap >= 0.0:
        # Candidate meets or exceeds seniority
        return max(70.0, round(100.0 - (gap * 10.0), 1))
    else:
        # Candidate has seniority deficit
        deficit = abs(gap)
        score = max(15.0, 100.0 - (deficit * 28.0))
        return round(score, 1)
