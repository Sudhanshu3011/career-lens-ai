"""
CareerLens AI - Seniority Domain Classifier

Classifies seniority tiers for:
1. Target Job Descriptions (JD Seniority) -> Determines active ROLE_WEIGHTS.
2. Candidate Profiles (Career Seniority) -> Detects actual professional duration and seniority.
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Dict, List, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)

SENIORITY_LABELS: Dict[str, str] = {
    "beginner": "Junior / Entry-Level",
    "mid_level": "Mid-Level",
    "senior": "Senior / Lead",
}

ROLE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "beginner": {
        "technical": 0.30,
        "experience": 0.10,
        "domain": 0.15,
        "education": 0.25,
        "evidence": 0.20,
    },
    "mid_level": {
        "technical": 0.25,
        "experience": 0.30,
        "domain": 0.20,
        "education": 0.05,
        "evidence": 0.20,
    },
    "senior": {
        "technical": 0.15,
        "experience": 0.35,
        "domain": 0.30,
        "education": 0.00,
        "evidence": 0.20,
    },
}

SENIOR_JD_CUES: List[str] = [
    "senior",
    "sr.",
    "sr ",
    "lead",
    "staff",
    "principal",
    "architect",
    "director",
    "head of",
    "vp",
    "5+ years",
    "6+ years",
    "7+ years",
    "8+ years",
    "10+ years",
    "minimum 5 years",
]

BEGINNER_JD_CUES: List[str] = [
    "junior",
    "jr.",
    "intern",
    "internship",
    "entry level",
    "entry-level",
    "graduate",
    "fresher",
    "trainee",
    "0-1 years",
    "0-2 years",
    "1-2 years",
]

SENIOR_TITLE_CUES: List[str] = [
    "senior",
    "sr.",
    "sr ",
    "lead",
    "staff",
    "principal",
    "architect",
    "director",
    "head of",
    "vp",
    "chief",
    "founder",
    "manager",
]

BEGINNER_TITLE_CUES: List[str] = [
    "intern",
    "internship",
    "junior",
    "jr.",
    "entry-level",
    "entry level",
    "student",
    "fresher",
    "trainee",
    "campus",
    "fellow",
    "apprentice",
]


class SeniorityClassifier:
    """Classifies Job Description and Candidate seniority tiers."""

    def __init__(self) -> None:
        self._jd_cache: Dict[str, Dict[str, Any]] = {}

    def classify_jd_seniority(
        self,
        job_description: str,
        job_role: str = "",
        laya_router: Any = None,
    ) -> Dict[str, Any]:
        """
        Classifies target job description into beginner, mid_level, or senior.
        Memoizes results to eliminate redundant forward passes on identical JDs in a batch.
        """
        clean_jd = (job_description or "").strip()
        clean_role = (job_role or "").strip()

        if not clean_jd and not clean_role:
            return {
                "seniority_tier": "mid_level",
                "seniority_label": SENIORITY_LABELS["mid_level"],
                "weights": ROLE_WEIGHTS["mid_level"],
                "probabilities": {},
                "decision_source": "default_empty_jd",
            }

        cache_key = f"{clean_role}|||{clean_jd}"
        if cache_key in self._jd_cache:
            return self._jd_cache[cache_key]

        eval_corpus = f"{clean_role} {clean_jd}".lower()
        explicit_tier: Optional[str] = None
        if any(cue in eval_corpus for cue in SENIOR_JD_CUES):
            explicit_tier = "senior"
        elif any(cue in eval_corpus for cue in BEGINNER_JD_CUES):
            explicit_tier = "beginner"

        if laya_router is not None:
            try:
                role_clause = f" for the '{clean_role}' position" if clean_role else ""
                question = {
                    "jd_seniority": {
                        "type": "choice",
                        "instructions": (
                            f"Determine the expected candidate seniority level demanded{role_clause} "
                            "based on required years of experience, job title, and scope of responsibilities."
                        ),
                        "criteria": {
                            "senior": "Senior, lead, staff, principal engineer, architect, or manager requiring 5+ years experience.",
                            "beginner": "Entry-level, junior, intern, associate role, or requiring 0-2 years experience.",
                            "mid_level": "Mid-level role requiring 2-5 years of independent professional experience.",
                        },
                    }
                }
                predict_text = (
                    f"Target Position: {clean_role}\n\nJob Description:\n{clean_jd}"
                    if clean_role and clean_role not in clean_jd
                    else clean_jd
                )
                res = laya_router.predict({"text": predict_text}, question)
                ans = res["answers"]["jd_seniority"]
                choice = ans.get("choice", "mid_level")
                probs = ans.get("probabilities", {})

                tier = explicit_tier or (
                    choice if choice in ROLE_WEIGHTS else "mid_level"
                )
                label = SENIORITY_LABELS.get(tier, "Mid-Level")
                logger.info(
                    f"Classified JD Seniority: tier='{tier}' ({label}), "
                    f"source='laya_model_calibrated' (explicit_cue={bool(explicit_tier)})"
                )
                result = {
                    "seniority_tier": tier,
                    "seniority_label": label,
                    "weights": ROLE_WEIGHTS[tier],
                    "probabilities": probs,
                    "decision_source": "laya_model_calibrated",
                }
                self._jd_cache[cache_key] = result
                return result
            except Exception as exc:
                logger.warning(
                    f"Laya JD seniority classification failed: {exc}. Using heuristic fallback."
                )

        tier = explicit_tier or "mid_level"
        label = SENIORITY_LABELS[tier]
        logger.info(
            f"Classified JD Seniority: tier='{tier}' ({label}), source='heuristic_fallback'"
        )
        fallback_res = {
            "seniority_tier": tier,
            "seniority_label": label,
            "weights": ROLE_WEIGHTS[tier],
            "probabilities": {},
            "decision_source": "heuristic_fallback",
        }
        self._jd_cache[cache_key] = fallback_res
        return fallback_res

    def classify_candidate_seniority(
        self,
        experience_text: str = "",
        summary_text: str = "",
        education_text: str = "",
        laya_router: Any = None,
    ) -> Dict[str, Any]:
        """
        Determines candidate's career level from resume history, calculating calendar span.
        """
        effective_exp = (
            experience_text.strip()
            if experience_text.strip()
            else "0 years (No professional work experience documented. Candidate is an active student / fresher / entry-level profile with academic projects only)."
        )
        candidate_text = (
            f"Candidate Work History & Professional Experience:\n{effective_exp}\n\n"
            f"Education & Academic Credentials:\n{education_text or 'None'}\n\n"
            f"Summary / Profile:\n{summary_text or 'None'}"
        )

        current_year = datetime.datetime.now().year
        years_found = [
            int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", experience_text)
        ]
        span_years = 0
        if years_found:
            valid_years = [y for y in years_found if 1990 <= y <= current_year]
            if valid_years:
                span_years = current_year - min(valid_years)

        if laya_router is not None:
            try:
                question = {
                    "candidate_seniority": {
                        "type": "choice",
                        "instructions": (
                            "Determine this candidate's career seniority tier based on their work history, "
                            "job titles, project responsibilities, and total years of professional experience."
                        ),
                        "criteria": {
                            "senior": "Senior, lead, staff, principal engineer, architect, director, or 5+ years of seasoned professional experience.",
                            "beginner": "Entry-level, junior, intern, student, recent graduate, fresher, or 0-2 years of professional experience.",
                            "mid_level": "Mid-level engineer or professional with 2-5 years of independent practical experience.",
                        },
                    }
                }
                res = laya_router.predict({"text": candidate_text}, question)
                ans = res["answers"]["candidate_seniority"]
                choice = ans.get("choice", "mid_level")
                probs = ans.get("probabilities", {})

                if choice in ROLE_WEIGHTS:
                    cand_label = SENIORITY_LABELS.get(choice, "Mid-Level")
                    logger.info(
                        f"Classified Candidate Seniority: tier='{choice}' ({cand_label}), "
                        f"source='laya_model' (calendar_span={span_years}y)"
                    )
                    return {
                        "seniority_tier": choice,
                        "seniority_label": cand_label,
                        "span_years": span_years,
                        "probabilities": probs,
                        "decision_source": "laya_model",
                    }
            except Exception as exc:
                logger.warning(
                    f"Laya candidate seniority classification failed: {exc}. Using deterministic fallback."
                )

        combined_lower = f"{summary_text}\n{experience_text}\n{education_text}".lower()
        has_senior = any(cue in combined_lower for cue in SENIOR_TITLE_CUES)
        has_beginner = any(cue in combined_lower for cue in BEGINNER_TITLE_CUES)

        explicit_years = [
            float(m)
            for m in re.findall(
                r"(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:exp|experience)?",
                combined_lower,
            )
        ]
        max_explicit_years = max(explicit_years) if explicit_years else 0.0

        if (
            span_years >= 5
            or max_explicit_years >= 5.0
            or (has_senior and span_years >= 3)
        ):
            tier = "senior"
        elif (
            span_years <= 1
            and max_explicit_years <= 1.0
            and not has_senior
            and (has_beginner or not experience_text.strip())
        ):
            tier = "beginner"
        elif has_beginner and span_years <= 2:
            tier = "beginner"
        else:
            tier = "mid_level"

        cand_label = SENIORITY_LABELS.get(tier, "Mid-Level")
        logger.info(
            f"Classified Candidate Seniority: tier='{tier}' ({cand_label}), "
            f"source='deterministic_fallback' (calendar_span={span_years}y, max_explicit_years={max_explicit_years})"
        )
        return {
            "seniority_tier": tier,
            "seniority_label": cand_label,
            "span_years": span_years,
            "probabilities": {},
            "decision_source": "deterministic_fallback",
        }


# Singleton instance
seniority_classifier = SeniorityClassifier()
