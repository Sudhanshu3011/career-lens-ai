"""
CareerLens AI - TypeSafe Confidence Gating
Calibrated confidence thresholding to control automated actions vs review escalation.
"""

from __future__ import annotations

from typing import List, Tuple


AUTOMATIC_THRESHOLD = 0.80
REVIEW_THRESHOLD = 0.55


def classify_confidence_tier(confidence: float) -> str:
    """
    Categorizes judgment confidence into actionable operational tiers:
    - AUTOMATIC: High certainty (>= 0.80). Automatic decision accepted.
    - UNCERTAIN: Moderate certainty (0.55 - 0.79). Decision permitted but flagged.
    - NEEDS_REVIEW: Low certainty (< 0.55). Escalated to human reviewer.
    """
    if confidence >= AUTOMATIC_THRESHOLD:
        return "AUTOMATIC"
    elif confidence >= REVIEW_THRESHOLD:
        return "UNCERTAIN"
    return "NEEDS_REVIEW"


def evaluate_batch_confidence(confidences: List[float]) -> Tuple[float, str, List[str]]:
    """
    Computes overall mean confidence across multi-factor judgments and generates review flags.
    """
    if not confidences:
        return 0.5, "UNCERTAIN", ["No confidence metrics returned by decision models."]

    mean_conf = round(sum(confidences) / len(confidences), 3)
    tier = classify_confidence_tier(mean_conf)
    flags: List[str] = []

    low_conf_count = sum(1 for c in confidences if c < REVIEW_THRESHOLD)
    if low_conf_count > 0:
        flags.append(f"{low_conf_count} evaluation dimension(s) have low confidence (< 0.55).")

    if tier == "NEEDS_REVIEW":
        flags.append("Overall confidence is below automatic acceptance threshold. Human review advised.")

    return mean_conf, tier, flags
