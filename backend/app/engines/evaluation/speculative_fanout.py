"""
CareerLens AI - Universal Speculative Fan-Out Evaluator
Calculates candidate fit score across any industry using dynamic System One answers.
Enforces strict gating invariants:
1. Core Domain Viability (<20% competency or unrelated background -> immediate flat REJECT, Score 0.0).
2. Mandatory Dealbreaker Veto (P < 0.40 -> Veto, capped <= 35.0, REJECT).
3. Weighted Composite Multipliers across all dimensions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.core.logger import get_logger
from app.models.domain.candidate_decision import (
    CandidateVerdict,
    GateResult,
    ScoreBreakdown,
)
from app.models.domain.resume_sections import ResumeParsedSections

logger = get_logger(__name__)

DEFAULT_MULTIPLIERS: Dict[str, float] = {
    "competency": 0.30,
    "seniority": 0.20,
    "experience": 0.20,
    "domain": 0.15,
    "evidence": 0.10,
    "education": 0.05,
}


def _extract_score_value(ans: Any, max_level: float = 5.0) -> float:
    """Extracts a normalized 0.0 - 100.0 percentage from a Score primitive answer."""
    if not ans:
        return 0.0
    if isinstance(ans, dict):
        raw_val = ans.get("score")
        if raw_val is None:
            raw_val = ans.get("value", 0.0)
    elif hasattr(ans, "score"):
        raw_val = ans.score
    else:
        try:
            raw_val = float(ans)
        except (ValueError, TypeError):
            raw_val = 0.0

    try:
        score_num = float(raw_val)
    except (ValueError, TypeError):
        score_num = 0.0

    return max(0.0, min(100.0, (score_num / max_level) * 100.0))


def _extract_choice_value(ans: Any) -> str:
    """Extracts choice key from a Choice primitive answer."""
    if not ans:
        return ""
    if isinstance(ans, dict):
        return str(ans.get("choice", "")).strip().lower()
    if hasattr(ans, "choice"):
        return str(ans.choice).strip().lower()
    return str(ans).strip().lower()


def _extract_noul_probability(ans: Any) -> float:
    """Extracts binary truth probability P(True) from a Noul primitive answer."""
    if not ans:
        return 0.5
    if isinstance(ans, dict):
        if "probability" in ans:
            return float(ans["probability"])
        if "noul" in ans:
            return 1.0 if ans["noul"] else 0.0
        return float(ans.get("confidence", 0.5))
    if hasattr(ans, "probability"):
        return float(ans.probability)
    if hasattr(ans, "noul"):
        return 1.0 if ans.noul else 0.0
    return 0.5


class SpeculativeFanoutEvaluator:
    """Universal Speculative Fan-Out Scorer and Gatekeeper."""

    def __init__(self, default_multipliers: Optional[Dict[str, float]] = None):
        self.multipliers = default_multipliers or DEFAULT_MULTIPLIERS

    def evaluate(
        self,
        candidate_sections: ResumeParsedSections,
        answers: Dict[str, Any],
        gate_registry: Dict[str, Dict[str, str]],
        custom_multipliers: Optional[Dict[str, float]] = None,
        engine_name: str = "jev",
    ) -> CandidateVerdict:
        """
        Evaluates candidate answers through the 3 speculative gates:
        Gate 1: Domain & Competency Viability
        Gate 2: Mandatory Dealbreaker Gates
        Gate 3: Multiplier Calculation
        """
        candidate_name = candidate_sections.candidate_name

        # 1. Parse Domain Alignment Choice
        domain_choice = _extract_choice_value(answers.get("domain_alignment"))
        if not domain_choice:
            domain_choice = "direct_domain_match"

        # 2. Parse Competency Depth Score (0-5)
        competency_pct = _extract_score_value(answers.get("competency_depth"), max_level=5.0)

        # 3. Parse Seniority Level Score (0-5)
        seniority_pct = _extract_score_value(answers.get("seniority_level"), max_level=5.0)

        # 4. Parse Evidence Quality Score (0-5)
        evidence_pct = _extract_score_value(answers.get("evidence_quality"), max_level=5.0)

        # --- GATE 1: Core Domain Viability ---
        # If candidate has unrelated background OR competency depth < 20%
        if domain_choice == "unrelated_background" or competency_pct < 20.0:
            logger.info(
                f"Candidate '{candidate_name}' failed Gate 1 (domain_choice={domain_choice}, competency={competency_pct:.1f}%). Flat REJECT."
            )
            return CandidateVerdict(
                candidate_name=candidate_name,
                fit_score=0.0,
                overall_decision="REJECT",
                domain_classification=domain_choice,
                breakdown=ScoreBreakdown(
                    competency_depth=round(competency_pct, 1),
                    seniority_fit=round(seniority_pct, 1),
                    experience_duration=0.0,
                    domain_alignment=0.0,
                    evidence_quality=round(evidence_pct, 1),
                    education_credentials=0.0,
                    raw_weighted_total=0.0,
                ),
                failed_hard_gates=[],
                passed_hard_gates=[],
                veto_reason="domain_competency_gate_failed",
                summary_feedback="Candidate does not meet the minimum required domain competencies or qualifications for this discipline.",
                engine_used=engine_name,
            )

        # --- GATE 2: Dealbreaker Noul Gates ---
        failed_gates: List[GateResult] = []
        failed_mandatory_gates: List[GateResult] = []
        passed_gates: List[GateResult] = []

        for gate_key, gate_meta in gate_registry.items():
            ans = answers.get(gate_key)
            prob = _extract_noul_probability(ans)
            passed = prob >= 0.40  # Dealbreaker threshold
            is_mandatory = gate_meta.get("is_mandatory", True)

            gate_res = GateResult(
                name=gate_meta.get("name", gate_key),
                question=gate_meta.get("question", ""),
                passed=passed,
                probability=round(prob, 3),
            )

            if passed:
                passed_gates.append(gate_res)
            else:
                failed_gates.append(gate_res)
                if is_mandatory:
                    failed_mandatory_gates.append(gate_res)

        # --- GATE 3: Multiplier Computation ---
        weights = {**self.multipliers, **(custom_multipliers or {})}
        total_w = sum(weights.values()) or 1.0

        # Calculate experience duration fit (Neural evaluation with timeline fallback)
        exp_ans = (
            answers.get("experience_duration")
            or answers.get("experience_duration_fit")
            or answers.get("experience_assessment")
        )
        if exp_ans is not None:
            exp_pct = _extract_score_value(exp_ans, max_level=5.0)
        else:
            num_roles = len(candidate_sections.work_experience)
            exp_pct = min(100.0, max(20.0, (num_roles / 3.0) * 80.0 + (seniority_pct * 0.2)))

        # Domain alignment score
        if domain_choice == "direct_domain_match":
            domain_pct = 100.0
        elif domain_choice == "adjacent_domain_transfer":
            domain_pct = 65.0
        else:
            domain_pct = 20.0

        # Education fit (Neural domain alignment evaluation with accredited degree fallback)
        edu_ans = (
            answers.get("education_credentials")
            or answers.get("education_domain_match")
            or answers.get("education_assessment")
        )
        if edu_ans is not None:
            edu_pct = _extract_score_value(edu_ans, max_level=5.0)
        else:
            edu_pct = 90.0 if candidate_sections.education else 50.0


        raw_weighted = (
            (weights.get("competency", 0.30) * competency_pct)
            + (weights.get("seniority", 0.20) * seniority_pct)
            + (weights.get("experience", 0.20) * exp_pct)
            + (weights.get("domain", 0.15) * domain_pct)
            + (weights.get("evidence", 0.10) * evidence_pct)
            + (weights.get("education", 0.05) * edu_pct)
        ) / total_w

        breakdown = ScoreBreakdown(
            competency_depth=round(competency_pct, 1),
            seniority_fit=round(seniority_pct, 1),
            experience_duration=round(exp_pct, 1),
            domain_alignment=round(domain_pct, 1),
            evidence_quality=round(evidence_pct, 1),
            education_credentials=round(edu_pct, 1),
            raw_weighted_total=round(raw_weighted, 1),
        )

        # Enforce Dealbreaker Veto Cap if any mandatory gate failed
        if failed_mandatory_gates:
            final_score = min(raw_weighted, 35.0)
            overall_decision = "REJECT"
            veto_reason = "mandatory_dealbreaker_failed"
            missing_names = ", ".join(g.name for g in failed_mandatory_gates)
            feedback = f"Candidate vetoed due to missing mandatory requirement(s): {missing_names}. Score capped at {final_score:.1f}%."
            logger.info(
                f"Candidate '{candidate_name}' failed {len(failed_mandatory_gates)} mandatory dealbreakers. Capped at {final_score:.1f}%."
            )
        else:
            final_score = raw_weighted
            veto_reason = None
            if final_score >= 70.0:
                overall_decision = "ADVANCE"
                feedback = "Strong match across domain competencies, seniority, and verified impact."
            elif final_score >= 50.0:
                overall_decision = "HOLD"
                feedback = "Potential match with minor gaps in seniority, specific domain tools, or quantifiable metrics."
            else:
                overall_decision = "REJECT"
                feedback = "Candidate overall fit is below competitive interview threshold."

        return CandidateVerdict(
            candidate_name=candidate_name,
            fit_score=round(final_score, 1),
            overall_decision=overall_decision,
            domain_classification=domain_choice,
            breakdown=breakdown,
            failed_hard_gates=failed_gates,
            passed_hard_gates=passed_gates,
            veto_reason=veto_reason,
            summary_feedback=feedback,
            engine_used=engine_name,
        )


# Global singleton instance
speculative_evaluator = SpeculativeFanoutEvaluator()
SpeculativeEvaluator = SpeculativeFanoutEvaluator
