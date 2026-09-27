"""
CareerLens AI - Calibrated Expected Quality Scorer

Eliminates the ~60% model score bias by computing calibrated mathematical expected value:
Score = max(0.0, 1.0 * P(high) + 0.35 * P(mid) - 0.60 * P(low))
- P(high) earns full credit.
- P(mid) earns partial credit (35%) reflecting adjacent/partial competencies.
- P(low) directly penalizes mismatch (-60%), driving unqualified profiles to 5%-25%.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from app.core.logger import get_logger

logger = get_logger(__name__)


def calculate_dimension_score(p_high: float, p_mid: float, p_low: float) -> float:
    """
    Computes calibrated continuous score from 3-class softmax probability distribution.
    Prevents artificial ~60% floors caused by neutral P(mid) bias.
    """
    raw_score = 1.0 * p_high + 0.35 * p_mid - 0.60 * p_low
    return round(max(0.0, min(1.0, raw_score)), 4)


def calculate_high_hits_penalty(high_hits: int) -> float:
    """
    Calibrated deduction penalizing candidates with few or no high hits across dimensions.
    Formula: max(0.0, (3 - H) * 0.02)
    - 0 hits: -0.06 (-6%)
    - 1 hit:  -0.04 (-4%)
    - 2 hits: -0.02 (-2%)
    - 3+ hits: 0.00 (no penalty)
    """
    return round(max(0.0, (3 - max(0, high_hits)) * 0.02), 4)


def resolve_decision(final_prob: float, high_hits: int) -> str:
    """Maps continuous probability and high hits count to categorical decision."""
    if final_prob >= 0.72 and high_hits >= 3:
        return "Strong match (High Probability)"
    elif final_prob >= 0.60 and high_hits >= 2:
        return "Moderate match (Weighted Balance)"
    elif final_prob >= 0.45:
        return "Borderline match (Requires review)"
    else:
        return "Poor fit (Deficits in key dimensions)"


class CalibratedScorer:
    """Evaluates multi-dimensional parameter answers into unified, calibrated scores."""

    def score_parameters(
        self,
        answers: Dict[str, Any],
        weights: Dict[str, float],
    ) -> Tuple[Dict[str, Any], int, float, float, float, str]:
        """
        Processes answers dictionary from Laya router or fallback rubric.
        Returns:
            (parameter_evaluations, high_hits_count, raw_weighted_prob, penalty, final_prob, decision)
        """
        parameter_evaluations: Dict[str, Any] = {}
        high_hits_count = 0
        raw_weighted_prob_sum = 0.0

        dimensions = ["technical", "experience", "domain", "education", "evidence"]
        for param in dimensions:
            ans = answers.get(param, {})
            probs = ans.get("probabilities", {})

            p_high = round(probs.get("high", 0.0), 4)
            p_mid = round(probs.get("mid", probs.get("medium", 0.0)), 4)
            p_low = round(probs.get("low", 0.0), 4)

            # Normalization fallback if sum != 1.0
            total_p = p_high + p_mid + p_low
            if total_p > 0 and abs(total_p - 1.0) > 0.01:
                p_high = round(p_high / total_p, 4)
                p_mid = round(p_mid / total_p, 4)
                p_low = round(p_low / total_p, 4)

            # Calibrated score calculation
            dimension_score = calculate_dimension_score(p_high, p_mid, p_low)
            weight = weights.get(param, 0.20)
            weighted_score = round(dimension_score * weight, 4)
            raw_weighted_prob_sum += weighted_score

            # High flag hit check: strictly requires high to be dominant
            is_high_hit = bool(p_high >= 0.40 and p_high > p_mid and p_high > p_low)
            if is_high_hit:
                high_hits_count += 1

            parameter_evaluations[param] = {
                "p_high": p_high,
                "p_mid": p_mid,
                "p_low": p_low,
                "selected_prob": round(max(p_high, p_mid), 4),
                "calibrated_score": dimension_score,
                "weight": weight,
                "weighted_score": weighted_score,
                "is_high_hit": is_high_hit,
                "percentage": int(round(dimension_score * 100)),
            }

        raw_weighted_prob = round(raw_weighted_prob_sum, 4)
        penalty = calculate_high_hits_penalty(high_hits_count)
        final_prob = round(max(0.0, raw_weighted_prob - penalty), 4)
        decision = resolve_decision(final_prob, high_hits_count)

        return (
            parameter_evaluations,
            high_hits_count,
            raw_weighted_prob,
            penalty,
            final_prob,
            decision,
        )


calibrated_scorer = CalibratedScorer()
