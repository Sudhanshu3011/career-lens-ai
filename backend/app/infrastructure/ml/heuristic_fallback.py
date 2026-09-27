"""
CareerLens AI - Heuristic Fallback Engine

Mathematical and rule-based fallback when Laya router or offline mode is active.
Constructs objective probability distributions from keyword coverage, metric density,
degree ontology, and chronology, then delegates to CalibratedScorer.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from app.core.logger import get_logger
from app.domain.scoring.calibrated_scorer import calibrated_scorer

logger = get_logger(__name__)

EDU_KEYWORDS: List[str] = [
    "bachelor",
    "master",
    "phd",
    "doctorate",
    "b.tech",
    "m.tech",
    "b.e",
    "m.e",
    "b.s",
    "m.s",
    "bs",
    "ms",
    "computer science",
    "engineering",
    "degree",
    "diploma",
    "graduate",
    "university",
    "college",
    "bca",
    "mca",
    "b.sc",
    "m.sc",
]


class HeuristicFallbackEngine:
    """Computes mathematical probability distributions without an ML model."""

    def evaluate(
        self,
        candidate_skills: Dict[str, Any],
        experience_text: str,
        job_description: str,
        education_text: str,
        weights: Dict[str, float],
        job_role: str = "",
        technical_overlap: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generates fallback answers dictionary and scores with CalibratedScorer."""
        clean_role = (job_role or "").strip()
        jd_lower = (
            f"{clean_role} {job_description}".lower()
            if clean_role
            else job_description.lower()
        )
        tech_skills = candidate_skills.get("technical_skills", [])
        tools = candidate_skills.get("tools_and_platforms", [])
        domains = candidate_skills.get("domains", [])
        all_candidate_skills = [s.lower() for s in tech_skills + tools]

        # 1. Technical match probability
        if technical_overlap and "skill_overlap_percentage" in technical_overlap:
            overlap_pct = technical_overlap["skill_overlap_percentage"] / 100.0
            p_tech_high = round(min(0.95, max(0.02, overlap_pct * 0.95)), 4)
            p_tech_low = round(min(0.95, max(0.02, (1.0 - overlap_pct) * 0.90)), 4)
            p_tech_mid = round(max(0.05, 1.0 - (p_tech_high + p_tech_low)), 4)
        else:
            matched_skills = [s for s in all_candidate_skills if s in jd_lower]
            tech_cov = (
                len(matched_skills) / max(1, len(all_candidate_skills))
                if all_candidate_skills
                else 0.1
            )
            p_tech_high = round(min(0.92, max(0.05, tech_cov * 0.85)), 4)
            p_tech_low = round(min(0.90, max(0.05, (1.0 - tech_cov) * 0.85)), 4)
            p_tech_mid = round(max(0.05, 1.0 - (p_tech_high + p_tech_low)), 4)

        # 2. Experience match probability
        exp_lower = experience_text.lower()
        exp_cues = [
            "year",
            "years",
            "senior",
            "lead",
            "architect",
            "developed",
            "managed",
            "built",
            "engineered",
        ]
        exp_count = sum(1 for c in exp_cues if c in exp_lower)
        p_exp_high = round(min(0.90, max(0.05, exp_count * 0.10 + 0.05)), 4)
        p_exp_low = round(max(0.05, 0.70 - p_exp_high * 0.6), 4)
        p_exp_mid = round(max(0.05, 1.0 - (p_exp_high + p_exp_low)), 4)

        # 3. Domain match probability
        domain_matches = [
            d
            for d in domains
            if any(term in jd_lower for term in d.lower().split() if len(term) > 2)
        ]
        dom_cov = len(domain_matches) / max(1, len(domains)) if domains else 0.1
        p_dom_high = round(min(0.90, max(0.05, dom_cov * 0.85)), 4)
        p_dom_low = round(max(0.05, 0.80 - p_dom_high * 0.7), 4)
        p_dom_mid = round(max(0.05, 1.0 - (p_dom_high + p_dom_low)), 4)

        # 4. Education match probability
        edu_lower = education_text.lower()
        has_edu = any(k in edu_lower for k in EDU_KEYWORDS)
        p_edu_high = 0.85 if has_edu else 0.15
        p_edu_low = 0.05 if has_edu else 0.65
        p_edu_mid = round(1.0 - (p_edu_high + p_edu_low), 4)

        # 5. Evidence match probability
        metrics = len(
            re.findall(
                r"\b\d+([%kKmMbB]|\s*(?:percent|ms|sec|users|customers|requests|reduction|increase|faster))\b",
                experience_text,
            )
        )
        p_evi_high = round(min(0.90, max(0.10, metrics * 0.15 + 0.10)), 4)
        p_evi_low = round(max(0.05, 0.75 - p_evi_high * 0.7), 4)
        p_evi_mid = round(max(0.05, 1.0 - (p_evi_high + p_evi_low)), 4)

        answers = {
            "technical": {
                "type": "choice",
                "choice": "high" if p_tech_high > p_tech_low else "low",
                "probabilities": {
                    "high": p_tech_high,
                    "mid": p_tech_mid,
                    "low": p_tech_low,
                },
            },
            "experience": {
                "type": "choice",
                "choice": "high" if p_exp_high > p_exp_low else "low",
                "probabilities": {
                    "high": p_exp_high,
                    "mid": p_exp_mid,
                    "low": p_exp_low,
                },
            },
            "domain": {
                "type": "choice",
                "choice": "high" if p_dom_high > p_dom_low else "low",
                "probabilities": {
                    "high": p_dom_high,
                    "mid": p_dom_mid,
                    "low": p_dom_low,
                },
            },
            "education": {
                "type": "choice",
                "choice": "high" if p_edu_high > p_edu_low else "low",
                "probabilities": {
                    "high": p_edu_high,
                    "mid": p_edu_mid,
                    "low": p_edu_low,
                },
            },
            "evidence": {
                "type": "choice",
                "choice": "high" if p_evi_high > p_evi_low else "low",
                "probabilities": {
                    "high": p_evi_high,
                    "mid": p_evi_mid,
                    "low": p_evi_low,
                },
            },
        }

        (
            param_evals,
            high_hits,
            raw_prob,
            penalty,
            final_prob,
            decision,
        ) = calibrated_scorer.score_parameters(answers, weights)

        return {
            "parameter_evaluations": param_evals,
            "raw_weighted_probability": raw_prob,
            "high_hits_count": high_hits,
            "penalty_applied": penalty,
            "total_weighted_probability": final_prob,
            "final_score": round(final_prob * 10.0, 2),
            "fit_score": round(final_prob * 100.0, 1),
            "overall_decision": decision,
            "breakdown": {p: param_evals[p]["percentage"] for p in param_evals},
            "source": "heuristic_calibrated_rubric",
            "telemetry": {
                "prompt_context": "heuristic_fallback",
                "questions": {},
                "raw_model_answers": answers,
            },
        }


heuristic_fallback = HeuristicFallbackEngine()
