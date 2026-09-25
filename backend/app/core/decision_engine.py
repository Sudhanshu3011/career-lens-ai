"""
CareerLens AI - Calibrated Laya Decision & Scoring Engine

Non-autoregressive candidate evaluation engine powered by ConvAI Innovations' Laya model.
Prioritizes JD seniority classification, dynamic 5-parameter weighting (ROLE_WEIGHTS),
max(P(high), P(mid)) selection, and unified scoring with calibrated least-high-hits penalty.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)

try:
    import laya
    _LAYA_AVAILABLE = True
except ImportError:
    _LAYA_AVAILABLE = False
    logger.warning("Laya library not available. Using calibrated mathematical decision fallback.")


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

SENIORITY_LABELS: Dict[str, str] = {
    "beginner": "Junior / Entry-Level",
    "mid_level": "Mid-Level",
    "senior": "Senior / Lead",
}


class LayaDecisionEngine:
    """
    Non-autoregressive Decision Engine utilizing ConvAI Innovations' Laya model
    for calibrated multi-dimensional candidate evaluation and seniority-weighted scoring.
    """

    _instance: Optional["LayaDecisionEngine"] = None

    def __init__(self) -> None:
        self.router = None
        if _LAYA_AVAILABLE:
            try:
                self.router = laya.Router(preload=False)
                logger.info("Laya Router initialized successfully in DecisionEngine")
            except Exception as exc:
                logger.warning(f"Failed to initialize Laya Router: {exc}. Using calibrated fallback.")

    @classmethod
    def get_instance(cls) -> "LayaDecisionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def _calculate_high_hits_penalty(high_hits: int) -> float:
        """
        Calibrated deduction penalizing candidates with few or no high hits across dimensions.
        Formula: max(0.0, (3 - H) * 0.02)
        - 0 hits: -0.06 (-6%)
        - 1 hit:  -0.04 (-4%)
        - 2 hits: -0.02 (-2%)
        - 3+ hits: 0.00 (no penalty)
        """
        return round(max(0.0, (3 - max(0, high_hits)) * 0.02), 4)

    def classify_jd_seniority(self, job_description: str, job_role: str = "") -> Dict[str, Any]:
        """
        Evaluates the target job description to classify required seniority into:
        - beginner: Junior / Entry-Level (0-2 years, interns, associates)
        - mid_level: Mid-Level (2-5 years, independent professional contributor)
        - senior: Senior / Lead (5+ years, architecture, leadership, principal/staff)
        Returns the selected tier, human-readable label, and active parameter weights.
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

        # Deterministic explicit keyword detection for high precision
        eval_corpus = f"{clean_role} {clean_jd}".lower()
        senior_cues = [
            "senior", "sr.", "sr ", "lead", "staff", "principal", "architect", "director", "head of",
            "5+ years", "6+ years", "7+ years", "8+ years", "10+ years", "minimum 5 years"
        ]
        beginner_cues = [
            "junior", "jr.", "intern", "internship", "entry level", "entry-level",
            "graduate", "fresher", "trainee", "0-1 years", "0-2 years", "1-2 years"
        ]

        explicit_tier = None
        if any(cue in eval_corpus for cue in senior_cues):
            explicit_tier = "senior"
        elif any(cue in eval_corpus for cue in beginner_cues):
            explicit_tier = "beginner"

        if self.router is not None:
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
                            "mid_level": "Mid-level role requiring 2-5 years of independent professional experience."
                        }
                    }
                }
                predict_text = (
                    f"Target Position: {clean_role}\n\nJob Description:\n{clean_jd}"
                    if clean_role and clean_role not in clean_jd
                    else clean_jd
                )
                res = self.router.predict({"text": predict_text}, question)
                ans = res["answers"]["jd_seniority"]
                choice = ans.get("choice", "mid_level")
                probs = ans.get("probabilities", {})

                # If explicit cues are unequivocal, prioritize them; otherwise use Laya model choice
                tier = explicit_tier or (choice if choice in ROLE_WEIGHTS else "mid_level")
                label = SENIORITY_LABELS.get(tier, "Mid-Level")
                logger.info(f"Classified JD Seniority: tier='{tier}' ({label}), source='laya_model_calibrated' (explicit_cue={bool(explicit_tier)})")
                return {
                    "seniority_tier": tier,
                    "seniority_label": label,
                    "weights": ROLE_WEIGHTS[tier],
                    "probabilities": probs,
                    "decision_source": "laya_model_calibrated",
                }
            except Exception as exc:
                logger.warning(f"Laya JD seniority classification failed: {exc}. Using heuristic fallback.")

        # Heuristic fallback if router unavailable
        tier = explicit_tier or "mid_level"
        label = SENIORITY_LABELS[tier]
        logger.info(f"Classified JD Seniority: tier='{tier}' ({label}), source='heuristic_fallback'")
        return {
            "seniority_tier": tier,
            "seniority_label": label,
            "weights": ROLE_WEIGHTS[tier],
            "probabilities": {},
            "decision_source": "heuristic_fallback",
        }

    def classify_candidate_seniority(
        self,
        experience_text: str = "",
        summary_text: str = "",
        education_text: str = "",
    ) -> Dict[str, Any]:
        """
        Determines the candidate's actual personal career seniority from their resume history.
        Primarily evaluates through Laya non-autoregressive decision model,
        using deterministic chronological and title heuristics as a resilient fallback.
        - beginner: Junior / Entry-Level (interns, students, fresh grads, 0-2 years)
        - mid_level: Mid-Level (2-5 years professional experience)
        - senior: Senior / Lead (5+ years, staff/principal, tech lead, manager, executive)
        """
        effective_exp = experience_text.strip() if experience_text.strip() else "0 years (No professional work experience documented. Candidate is an active student / fresher / entry-level profile with academic projects only)."
        candidate_text = (
            f"Candidate Work History & Professional Experience:\n{effective_exp}\n\n"
            f"Education & Academic Credentials:\n{education_text or 'None'}\n\n"
            f"Summary / Profile:\n{summary_text or 'None'}"
        )

        # Calculate calendar years span for context and fallback
        import re
        import datetime
        current_year = datetime.datetime.now().year

        years_found = [int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", experience_text)]
        span_years = 0
        if years_found:
            valid_years = [y for y in years_found if 1990 <= y <= current_year]
            if valid_years:
                span_years = current_year - min(valid_years)

        # Primary Path: Laya non-autoregressive decision router
        if self.router is not None:
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
                            "mid_level": "Mid-level engineer or professional with 2-5 years of independent practical experience."
                        }
                    }
                }
                res = self.router.predict({"text": candidate_text}, question)
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
                logger.warning(f"Laya candidate seniority classification failed: {exc}. Using deterministic fallback.")

        # Fallback: Deterministic chronological and title heuristic analysis
        combined_lower = f"{summary_text}\n{experience_text}\n{education_text}".lower()
        senior_title_cues = [
            "senior", "sr.", "sr ", "lead", "staff", "principal", "architect",
            "director", "head of", "vp", "chief", "founder", "manager"
        ]
        beginner_title_cues = [
            "intern", "internship", "junior", "jr.", "entry-level", "entry level",
            "student", "fresher", "trainee", "campus", "fellow", "graduate trainee",
            "2024", "2025", "2026", "2027"
        ]

        has_senior = any(cue in combined_lower for cue in senior_title_cues)
        has_beginner = any(cue in combined_lower for cue in beginner_title_cues)

        years_matches = [int(y) for y in re.findall(r"(\d+)\+?\s*(?:years|yrs)", combined_lower) if int(y) < 40]
        max_explicit_years = max(years_matches) if years_matches else 0

        if not experience_text.strip() and has_beginner:
            tier = "beginner"
        elif max_explicit_years >= 5 or span_years >= 6 or (has_senior and span_years >= 4):
            tier = "senior"
        elif (has_beginner and span_years <= 2) or (not has_senior and span_years < 2 and max_explicit_years < 2):
            tier = "beginner"
        elif max_explicit_years >= 2 or span_years >= 2:
            tier = "mid_level"
        elif has_senior:
            tier = "senior"
        elif has_beginner:
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

    def evaluate_resume_match(
        self,
        candidate_skills: Dict[str, Any],
        experience_text: str,
        job_description: str,
        education_text: str = "",
        job_role: str = "",
    ) -> Dict[str, Any]:
        """
        Evaluates candidate match against target job description:
        1. Classifies JD seniority -> triggers ROLE_WEIGHTS.
        2. Classifies candidate's personal seniority -> detects career level.
        3. Evaluates 5 parameters: technical, experience, domain, education, evidence.
        4. For each parameter: selects max(P(high), P(mid)) * weight and flags high hits.
        5. Applies calibrated penalty for least high hits: penalty = max(0.0, (3 - H) * 0.02).
        6. Computes final unified score and decision.
        """
        clean_role = (job_role or "").strip()
        # Step 1: Pre-assess JD Seniority and activate weights
        jd_seniority_info = self.classify_jd_seniority(job_description, job_role=clean_role)
        tier = jd_seniority_info["seniority_tier"]
        weights = jd_seniority_info["weights"]

        # Prepare evaluation contexts
        tech_skills = candidate_skills.get("technical_skills", [])
        tools = candidate_skills.get("tools_and_platforms", [])
        domains = candidate_skills.get("domains", [])

        cand_edu = (
            education_text
            or candidate_skills.get("education")
            or candidate_skills.get("education_text")
            or ""
        )
        if isinstance(cand_edu, list):
            cand_edu = ", ".join(str(item) for item in cand_edu)
        effective_education = cand_edu.strip()

        clean_exp = experience_text.strip()
        effective_experience = clean_exp if clean_exp else "None. Candidate has 0 years of professional work experience (student/fresher profile with academic projects only)."

        candidate_summary = (
            f"Candidate Technical Skills: {', '.join(tech_skills)}\n"
            f"Tools & Platforms: {', '.join(tools)}\n"
            f"Domains: {', '.join(domains)}\n"
            f"Education: {effective_education}\n"
            f"Experience: {effective_experience}"
        )

        # Step 2: Classify candidate's personal seniority from resume
        cand_seniority_info = self.classify_candidate_seniority(
            experience_text=clean_exp,
            summary_text=candidate_summary,
            education_text=effective_education,
        )

        role_header = f"Target Position: {clean_role}\n\n" if clean_role else ""
        state = {
            "combined_context": f"{role_header}Job Description:\n{job_description}\n\nCandidate Profile:\n{candidate_summary}",
        }

        if self.router is not None:
            try:
                return self._predict_with_laya(
                    state=state,
                    jd_seniority_info=jd_seniority_info,
                    cand_seniority_info=cand_seniority_info,
                    weights=weights,
                    tech_skills=tech_skills,
                    job_role=clean_role,
                )
            except Exception as exc:
                logger.warning(f"Laya evaluation prediction failed: {exc}. Using calibrated fallback.")

        return self._predict_with_calibrated_rubric(
            candidate_skills=candidate_skills,
            experience_text=experience_text,
            job_description=job_description,
            education_text=effective_education,
            jd_seniority_info=jd_seniority_info,
            cand_seniority_info=cand_seniority_info,
            weights=weights,
            job_role=clean_role,
        )

    def _predict_with_laya(
        self,
        state: Dict[str, str],
        jd_seniority_info: Dict[str, Any],
        weights: Dict[str, float],
        tech_skills: List[str],
        cand_seniority_info: Optional[Dict[str, Any]] = None,
        job_role: str = "",
    ) -> Dict[str, Any]:
        """Runs the 5 non-autoregressive Laya parameter questions with dynamically injected target role."""
        clean_role = (job_role or "").strip()
        role_target = f"for the '{clean_role}' position" if clean_role else "for this position"
        role_noun = f"the {clean_role} role" if clean_role else "the target role"
        role_title = f"as a {clean_role}" if clean_role else "for the target role"

        questions = {
            "technical": {
                "type": "choice",
                "instructions": (
                    f"Evaluate how thoroughly the candidate's technical skills, languages, and frameworks "
                    f"satisfy the core technical requirements {role_target}."
                ),
                "criteria": {
                    "high": f"Matches nearly all or all essential technical skills and frameworks required {role_target}.",
                    "mid": f"Matches a substantial portion of skills for {role_noun} but misses some key technologies.",
                    "low": f"Matches few or none of the required technical skills for {role_noun}."
                }
            },
            "experience": {
                "type": "choice",
                "instructions": (
                    f"Evaluate the candidate's professional experience, seniority, and role responsibilities "
                    f"against the seniority and duties demanded {role_target}."
                ),
                "criteria": {
                    "high": f"Experience level, duties, and seniority strongly meet or exceed expectations {role_target}.",
                    "mid": f"Relevant background, but experience is somewhat junior, partial, or adjacent {role_target}.",
                    "low": f"Insufficient relevant experience or significant seniority mismatch {role_target}."
                }
            },
            "domain": {
                "type": "choice",
                "instructions": (
                    f"Evaluate whether the candidate's industry domain and problem spaces align with "
                    f"the industry, problem domain, and architecture demanded by {role_noun}."
                ),
                "criteria": {
                    "high": f"Directly identical industry domain and architectural specializations relevant to {role_noun}.",
                    "mid": f"Related technical domain with transferable principles to {role_noun}.",
                    "low": f"Completely unrelated domain with minimal overlap to {role_noun}."
                }
            },
            "education": {
                "type": "choice",
                "instructions": (
                    f"Evaluate the candidate's academic degrees, educational background, and foundational credentials "
                    f"against the standards expected for {role_noun}."
                ),
                "criteria": {
                    "high": f"Holds required or advanced degrees (e.g. Master's/PhD or Bachelor's in CS/related field) with strong alignment for {role_noun}.",
                    "mid": f"Holds related degree or relevant certifications with partial alignment for {role_noun}.",
                    "low": f"No relevant degree or education credentials mentioned for {role_noun}."
                }
            },
            "evidence": {
                "type": "choice",
                "instructions": (
                    f"Evaluate the strength and concreteness of evidence in the candidate's work history "
                    f"demonstrating measurable impact and competence {role_title}."
                ),
                "criteria": {
                    "high": f"Strong concrete evidence with clear metrics, ownership, and measurable impact {role_title}.",
                    "mid": f"Moderate evidence with descriptive responsibilities but fewer quantifiable metrics {role_title}.",
                    "low": f"Vague, passive, or unsubstantiated bullet points lacking demonstrable impact {role_title}."
                }
            },
        }

        result = self.router.predict({"text": state["combined_context"]}, questions)
        answers = result.get("answers", {})

        parameter_evaluations: Dict[str, Any] = {}
        high_hits_count = 0
        raw_weighted_prob_sum = 0.0

        for param in ["technical", "experience", "domain", "education", "evidence"]:
            ans = answers.get(param, {})
            probs = ans.get("probabilities", {})
            p_high = round(probs.get("high", 0.0), 4)
            p_mid = round(probs.get("mid", probs.get("medium", 0.0)), 4)
            p_low = round(probs.get("low", 0.0), 4)

            # Core logic: max of high and mid probability
            selected_prob = round(max(p_high, p_mid), 4)
            weight = weights.get(param, 0.20)
            weighted_score = round(selected_prob * weight, 4)
            raw_weighted_prob_sum += weighted_score

            # High flag hit check
            is_high_hit = bool(p_high >= p_mid and p_high > p_low and p_high > 0.33)
            if is_high_hit:
                high_hits_count += 1

            parameter_evaluations[param] = {
                "p_high": p_high,
                "p_mid": p_mid,
                "p_low": p_low,
                "selected_prob": selected_prob,
                "weight": weight,
                "weighted_score": weighted_score,
                "is_high_hit": is_high_hit,
                "percentage": int(round(selected_prob * 100)),
            }

        raw_weighted_prob = round(raw_weighted_prob_sum, 4)
        penalty = self._calculate_high_hits_penalty(high_hits_count)
        final_prob = round(max(0.0, raw_weighted_prob - penalty), 4)
        final_score = round(final_prob * 10.0, 2)
        fit_score_pct = round(final_prob * 100.0, 1)

        decision = self._resolve_decision(final_prob, high_hits_count)

        breakdown = {
            "technical_requirements": parameter_evaluations["technical"]["percentage"],
            "experience_requirements": parameter_evaluations["experience"]["percentage"],
            "domain_alignment": parameter_evaluations["domain"]["percentage"],
            "education_alignment": parameter_evaluations["education"]["percentage"],
            "evidence_strength": parameter_evaluations["evidence"]["percentage"],
        }

        cand_tier = (cand_seniority_info or {}).get("seniority_tier", "mid_level")
        cand_label = (cand_seniority_info or {}).get("seniority_label", "Mid-Level")

        logger.info(
            f"Laya Decision Evaluation: raw_prob={raw_weighted_prob:.3f}, penalty=-{penalty*100:.0f}%, "
            f"final_prob={final_prob:.3f}, fit_score={fit_score_pct}%, high_hits={high_hits_count}/5, "
            f"decision='{decision}', cand_seniority='{cand_label}'"
        )

        return {
            "seniority_tier": jd_seniority_info["seniority_tier"],
            "seniority_label": jd_seniority_info["seniority_label"],
            "target_seniority_tier": jd_seniority_info["seniority_tier"],
            "target_seniority_label": jd_seniority_info["seniority_label"],
            "candidate_seniority_tier": cand_tier,
            "candidate_seniority_label": cand_label,
            "role_weights": weights,
            "parameter_evaluations": parameter_evaluations,
            "raw_weighted_probability": raw_weighted_prob,
            "high_hits_count": high_hits_count,
            "penalty_applied": penalty,
            "total_weighted_probability": final_prob,
            "final_score": final_score,
            "fit_score": fit_score_pct,
            "overall_decision": decision,
            "breakdown": breakdown,
            "source": "laya_model",
        }

    def _predict_with_calibrated_rubric(
        self,
        candidate_skills: Dict[str, Any],
        experience_text: str,
        job_description: str,
        education_text: str,
        jd_seniority_info: Dict[str, Any],
        weights: Dict[str, float],
        cand_seniority_info: Optional[Dict[str, Any]] = None,
        job_role: str = "",
    ) -> Dict[str, Any]:
        """Mathematical fallback executing identical probability selection and penalty formulas."""
        clean_role = (job_role or "").strip()
        jd_lower = f"{clean_role} {job_description}".lower() if clean_role else job_description.lower()
        tech_skills = candidate_skills.get("technical_skills", [])
        tools = candidate_skills.get("tools_and_platforms", [])
        domains = candidate_skills.get("domains", [])
        all_candidate_skills = [s.lower() for s in tech_skills + tools]

        # 1. Technical match probability
        matched_skills = [s for s in all_candidate_skills if s in jd_lower]
        tech_cov = len(matched_skills) / max(1, len(all_candidate_skills)) if all_candidate_skills else 0.2
        p_tech_high = min(0.95, max(0.05, tech_cov * 0.90 + 0.05))
        p_tech_mid = min(0.90, max(0.10, 1.0 - p_tech_high * 0.8))
        p_tech_low = max(0.02, 1.0 - (p_tech_high + p_tech_mid) / 2)

        # 2. Experience match probability
        exp_lower = experience_text.lower()
        exp_cues = ["year", "years", "senior", "lead", "architect", "developed", "managed", "built", "engineered"]
        exp_count = sum(1 for c in exp_cues if c in exp_lower)
        p_exp_high = min(0.92, max(0.10, exp_count * 0.12 + 0.10))
        p_exp_mid = min(0.85, max(0.15, 0.70))
        p_exp_low = max(0.05, 0.20)

        # 3. Domain match probability
        domain_matches = [d for d in domains if any(term in jd_lower for term in d.lower().split() if len(term) > 2)]
        dom_cov = len(domain_matches) / max(1, len(domains)) if domains else 0.3
        p_dom_high = min(0.90, max(0.10, dom_cov * 0.85 + 0.10))
        p_dom_mid = 0.65
        p_dom_low = 0.20

        # 4. Education match probability
        edu_lower = education_text.lower()
        edu_keywords = [
            "bachelor", "master", "phd", "doctorate", "b.tech", "m.tech", "b.e", "m.e",
            "b.s", "m.s", "bs", "ms", "computer science", "engineering", "degree",
            "diploma", "graduate", "university", "college", "bca", "mca", "b.sc", "m.sc"
        ]
        has_edu = any(k in edu_lower for k in edu_keywords)
        p_edu_high = 0.88 if has_edu else 0.25
        p_edu_mid = 0.70 if has_edu else 0.50
        p_edu_low = 0.10 if has_edu else 0.50

        # 5. Evidence match probability
        metrics = len(re.findall(r"\b\d+([%kKmMbB]|\s*(?:percent|ms|sec|users|customers|requests|reduction|increase|faster))\b", experience_text))
        p_evi_high = min(0.90, max(0.15, metrics * 0.15 + 0.25))
        p_evi_mid = 0.65
        p_evi_low = 0.20

        raw_probs = {
            "technical": (p_tech_high, p_tech_mid, p_tech_low),
            "experience": (p_exp_high, p_exp_mid, p_exp_low),
            "domain": (p_dom_high, p_dom_mid, p_dom_low),
            "education": (p_edu_high, p_edu_mid, p_edu_low),
            "evidence": (p_evi_high, p_evi_mid, p_evi_low),
        }

        parameter_evaluations: Dict[str, Any] = {}
        high_hits_count = 0
        raw_weighted_prob_sum = 0.0

        for param in ["technical", "experience", "domain", "education", "evidence"]:
            p_h, p_m, p_l = raw_probs[param]
            p_high = round(p_h, 4)
            p_mid = round(p_m, 4)
            p_low = round(p_l, 4)

            selected_prob = round(max(p_high, p_mid), 4)
            weight = weights.get(param, 0.20)
            weighted_score = round(selected_prob * weight, 4)
            raw_weighted_prob_sum += weighted_score

            is_high_hit = bool(p_high >= p_mid and p_high > p_low and p_high > 0.33)
            if is_high_hit:
                high_hits_count += 1

            parameter_evaluations[param] = {
                "p_high": p_high,
                "p_mid": p_mid,
                "p_low": p_low,
                "selected_prob": selected_prob,
                "weight": weight,
                "weighted_score": weighted_score,
                "is_high_hit": is_high_hit,
                "percentage": int(round(selected_prob * 100)),
            }

        raw_weighted_prob = round(raw_weighted_prob_sum, 4)
        penalty = self._calculate_high_hits_penalty(high_hits_count)
        final_prob = round(max(0.0, raw_weighted_prob - penalty), 4)
        final_score = round(final_prob * 10.0, 2)
        fit_score_pct = round(final_prob * 100.0, 1)

        decision = self._resolve_decision(final_prob, high_hits_count)

        breakdown = {
            "technical_requirements": parameter_evaluations["technical"]["percentage"],
            "experience_requirements": parameter_evaluations["experience"]["percentage"],
            "domain_alignment": parameter_evaluations["domain"]["percentage"],
            "education_alignment": parameter_evaluations["education"]["percentage"],
            "evidence_strength": parameter_evaluations["evidence"]["percentage"],
        }

        cand_tier = (cand_seniority_info or {}).get("seniority_tier", "mid_level")
        cand_label = (cand_seniority_info or {}).get("seniority_label", "Mid-Level")

        logger.info(
            f"Calibrated Rubric Evaluation: raw_prob={raw_weighted_prob:.3f}, penalty=-{penalty*100:.0f}%, "
            f"final_prob={final_prob:.3f}, fit_score={fit_score_pct}%, high_hits={high_hits_count}/5, "
            f"decision='{decision}', cand_seniority='{cand_label}'"
        )

        return {
            "seniority_tier": jd_seniority_info["seniority_tier"],
            "seniority_label": jd_seniority_info["seniority_label"],
            "target_seniority_tier": jd_seniority_info["seniority_tier"],
            "target_seniority_label": jd_seniority_info["seniority_label"],
            "candidate_seniority_tier": cand_tier,
            "candidate_seniority_label": cand_label,
            "role_weights": weights,
            "parameter_evaluations": parameter_evaluations,
            "raw_weighted_probability": raw_weighted_prob,
            "high_hits_count": high_hits_count,
            "penalty_applied": penalty,
            "total_weighted_probability": final_prob,
            "final_score": final_score,
            "fit_score": fit_score_pct,
            "overall_decision": decision,
            "breakdown": breakdown,
            "source": "calibrated_rubric",
        }

    @staticmethod
    def _resolve_decision(final_prob: float, high_hits: int) -> str:
        """Resolves overall recommendation decision from unified penalized probability."""
        if final_prob >= 0.72 and high_hits >= 2:
            return "Strong match"
        elif final_prob >= 0.52:
            return "Moderate match"
        elif final_prob >= 0.35:
            return "Weak match"
        return "Poor match"


decision_engine = LayaDecisionEngine.get_instance()
