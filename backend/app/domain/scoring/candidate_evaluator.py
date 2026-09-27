"""
CareerLens AI - Candidate Match Evaluator

Domain service coordinating:
1. Target Job Description Seniority & Role Weights.
2. Candidate Career Seniority Assessment.
3. Ground-Truth Anchored ML Inference via LayaClient.
4. Calibrated Multi-Dimensional Expected Quality Scoring.
5. Telemetry Capture for complete auditability.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.core.logger import get_logger
from app.domain.scoring.calibrated_scorer import calibrated_scorer
from app.domain.seniority.classifier import seniority_classifier
from app.infrastructure.ml.heuristic_fallback import heuristic_fallback
from app.infrastructure.ml.laya_client import laya_client
from app.infrastructure.ml.prompt_templates import (
    build_candidate_prompt,
    build_parameter_questions,
)
from app.infrastructure.telemetry.laya_telemetry import LayaTelemetry

logger = get_logger(__name__)


class CandidateEvaluator:
    """Evaluates candidate fit against target requisition using calibrated decision logic."""

    def evaluate(
        self,
        candidate_skills: Dict[str, Any],
        experience_text: str,
        job_description: str,
        education_text: str = "",
        job_role: str = "",
        technical_overlap: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes complete multi-dimensional match evaluation:
        1. Classifies JD seniority & activates weights.
        2. Classifies candidate career level.
        3. Formulates anchored prompt & 5 parameter questions.
        4. Runs Laya non-autoregressive forward pass with telemetry.
        5. Computes calibrated score & high-hits penalty.
        """
        clean_role = (job_role or "").strip()

        # Step 1: Pre-assess JD Seniority & activate role weights (cached)
        jd_seniority_info = seniority_classifier.classify_jd_seniority(
            job_description=job_description,
            job_role=clean_role,
            laya_router=laya_client.router,
        )
        weights = jd_seniority_info["weights"]

        # Step 2: Context Extraction & Formatting
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
        effective_experience = (
            clean_exp
            if clean_exp
            else "None. Candidate has 0 years of professional work experience (student/fresher profile with academic projects only)."
        )

        candidate_summary = (
            f"Candidate Technical Skills: {', '.join(tech_skills)}\n"
            f"Tools & Platforms: {', '.join(tools)}\n"
            f"Domains: {', '.join(domains)}\n"
            f"Education: {effective_education}\n"
            f"Experience: {effective_experience}"
        )

        # Step 3: Classify Candidate's Personal Seniority
        cand_seniority_info = seniority_classifier.classify_candidate_seniority(
            experience_text=clean_exp,
            summary_text=candidate_summary,
            education_text=effective_education,
            laya_router=laya_client.router,
        )

        # Step 4: ML Inference with Ground-Truth Anchoring
        if laya_client.is_available:
            try:
                prompt_text = build_candidate_prompt(
                    job_description=job_description,
                    job_role=clean_role,
                    tech_skills=tech_skills,
                    tools=tools,
                    domains=domains,
                    education_text=effective_education,
                    experience_text=clean_exp,
                    technical_overlap=technical_overlap,
                )
                questions = build_parameter_questions(job_role=clean_role)

                answers, telemetry = laya_client.predict(prompt_text, questions)

                (
                    param_evals,
                    high_hits,
                    raw_prob,
                    penalty,
                    final_prob,
                    decision,
                ) = calibrated_scorer.score_parameters(answers, weights)

                logger.info(
                    f"Laya Decision Evaluation: raw_prob={raw_prob:.3f}, penalty=-{penalty*100:.0f}%, "
                    f"final_prob={final_prob:.3f}, fit_score={final_prob*100:.1f}%, high_hits={high_hits}/5, "
                    f"decision='{decision}', cand_seniority='{cand_seniority_info['seniority_label']}'"
                )

                return {
                    "seniority_tier": jd_seniority_info["seniority_tier"],
                    "seniority_label": jd_seniority_info["seniority_label"],
                    "target_seniority_tier": jd_seniority_info["seniority_tier"],
                    "target_seniority_label": jd_seniority_info["seniority_label"],
                    "candidate_seniority_tier": cand_seniority_info["seniority_tier"],
                    "candidate_seniority_label": cand_seniority_info["seniority_label"],
                    "role_weights": weights,
                    "parameter_evaluations": param_evals,
                    "raw_weighted_probability": raw_prob,
                    "high_hits_count": high_hits,
                    "penalty_applied": penalty,
                    "total_weighted_probability": final_prob,
                    "final_score": round(final_prob * 10.0, 2),
                    "fit_score": round(final_prob * 100.0, 1),
                    "overall_decision": decision,
                    "breakdown": {
                        "technical_requirements": param_evals.get("technical", {}).get(
                            "percentage", 0
                        ),
                        "experience_requirements": param_evals.get(
                            "experience", {}
                        ).get("percentage", 0),
                        "domain_alignment": param_evals.get("domain", {}).get(
                            "percentage", 0
                        ),
                        "education_alignment": param_evals.get("education", {}).get(
                            "percentage", 70
                        ),
                        "evidence_strength": param_evals.get("evidence", {}).get(
                            "percentage", 0
                        ),
                        "technical": param_evals.get("technical", {}).get(
                            "percentage", 0
                        ),
                        "experience": param_evals.get("experience", {}).get(
                            "percentage", 0
                        ),
                        "domain": param_evals.get("domain", {}).get("percentage", 0),
                        "education": param_evals.get("education", {}).get(
                            "percentage", 70
                        ),
                        "evidence": param_evals.get("evidence", {}).get(
                            "percentage", 0
                        ),
                    },
                    "source": "laya_model",
                    "telemetry": telemetry.to_dict(),
                }
            except Exception as exc:
                logger.warning(
                    f"Laya evaluation prediction failed: {exc}. Using calibrated heuristic fallback."
                )

        # Fallback path if model unavailable
        fb_res = heuristic_fallback.evaluate(
            candidate_skills=candidate_skills,
            experience_text=clean_exp,
            job_description=job_description,
            education_text=effective_education,
            weights=weights,
            job_role=clean_role,
            technical_overlap=technical_overlap,
        )
        fb_res["seniority_tier"] = jd_seniority_info["seniority_tier"]
        fb_res["seniority_label"] = jd_seniority_info["seniority_label"]
        fb_res["target_seniority_tier"] = jd_seniority_info["seniority_tier"]
        fb_res["target_seniority_label"] = jd_seniority_info["seniority_label"]
        fb_res["candidate_seniority_tier"] = cand_seniority_info["seniority_tier"]
        fb_res["candidate_seniority_label"] = cand_seniority_info["seniority_label"]
        fb_res["role_weights"] = weights
        return fb_res


candidate_evaluator = CandidateEvaluator()
