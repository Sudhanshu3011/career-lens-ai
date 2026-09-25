"""
CareerLens AI - Candidate vs. Job Description Scorer

Evaluates candidate competencies against target job requirements using
deterministic technical keyword taxonomy and Laya non-autoregressive decision models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.tools.tech_keyword_extractor import extract_tech_keywords
from app.core.decision_engine import decision_engine
from app.core.logger import get_logger

logger = get_logger(__name__)


def score_resume_against_jd(
    resume_data: Dict[str, Any],
    job_description: str,
    job_role: str = "",
) -> Dict[str, Any]:
    """
    Evaluates candidate resume against target job description.

    1. Extracts technical competencies from JD using 450+ IT skill taxonomy.
    2. Measures technical overlap, missing requirements, and candidate bonus skills.
    3. Assesses JD seniority tier and activates dynamic ROLE_WEIGHTS.
    4. Evaluates 5 dimensions: Technical, Experience, Domain, Education, Evidence.
    5. Calculates weighted probability, applies least-high-hits penalty, and generates unified score.
    """
    if not job_description or not job_description.strip():
        return {
            "final_score": 0.0,
            "fit_score": 0.0,
            "overall_decision": "No Job Description Provided",
            "seniority_tier": "mid_level",
            "seniority_label": "Mid-Level",
            "role_weights": {},
            "parameter_evaluations": {},
            "raw_weighted_probability": 0.0,
            "high_hits_count": 0,
            "penalty_applied": 0.0,
            "total_weighted_probability": 0.0,
            "breakdown": {
                "technical_requirements": 0,
                "experience_requirements": 0,
                "domain_alignment": 0,
                "education_alignment": 0,
                "evidence_strength": 0,
            },
            "technical_overlap": {
                "jd_skills_required": [],
                "matched_skills": [],
                "missing_jd_skills": [],
                "candidate_bonus_skills": [],
                "skill_overlap_percentage": 0.0,
            },
            "source": "empty_jd",
        }

    # 1. Extract technical requirements from target Job Description
    jd_analysis = extract_tech_keywords(job_description)
    jd_skills: List[str] = jd_analysis.get("extracted_skills", [])

    # 2. Extract or retrieve candidate skills
    cand_skills: List[str] = resume_data.get("tech_skills", [])
    if not cand_skills and "raw_text" in resume_data:
        cand_analysis = extract_tech_keywords(resume_data["raw_text"])
        cand_skills = cand_analysis.get("extracted_skills", [])

    # 3. Compute deterministic technical overlap
    cand_lower = {s.lower(): s for s in cand_skills}
    jd_lower = {s.lower(): s for s in jd_skills}

    matched_skills = [jd_lower[k] for k in jd_lower if k in cand_lower]
    missing_jd_skills = [jd_lower[k] for k in jd_lower if k not in cand_lower]
    candidate_bonus = [cand_lower[k] for k in cand_lower if k not in jd_lower]

    overlap_pct = (
        round((len(matched_skills) / max(1, len(jd_skills))) * 100, 1)
        if jd_skills
        else 100.0
    )
    logger.debug(
        f"Technical overlap: JD={len(jd_skills)} skills, Cand={len(cand_skills)} skills | "
        f"Matched={len(matched_skills)} ({overlap_pct}%), Missing={len(missing_jd_skills)}"
    )

    # 4. Prepare parameters for Decision Engine
    tools = resume_data.get("tools_and_platforms", [])
    domains = resume_data.get("domains") or list(
        resume_data.get("skills_by_domain", {}).keys()
    )
    experience_text = (
        resume_data.get("experience", "")
        or resume_data.get("summary", "")
        or resume_data.get("raw_text", "")
    )
    education_text = (
        resume_data.get("education", "")
        or resume_data.get("academic_background", "")
        or ""
    )

    candidate_skills_dict = {
        "technical_skills": cand_skills,
        "tools_and_platforms": tools,
        "domains": domains,
        "education": education_text,
    }

    # 5. Execute decision model
    laya_eval = decision_engine.evaluate_resume_match(
        candidate_skills=candidate_skills_dict,
        experience_text=experience_text,
        job_description=job_description,
        education_text=education_text,
        job_role=job_role,
    )

    laya_fit_score = laya_eval.get("fit_score", 70.0)
    skill_overlap_pct = overlap_pct

    # Equally weight skill overlap (50%) and Laya multi-dimensional probability score (50%)
    combined_fit_score = round(0.50 * laya_fit_score + 0.50 * skill_overlap_pct, 1)
    combined_final_score = round(combined_fit_score / 10.0, 2)
    combined_weighted_prob = round(combined_fit_score / 100.0, 4)

    logger.debug(
        f"Scoring combination: LayaFit={laya_fit_score}% (50%), Overlap={skill_overlap_pct}% (50%) "
        f"-> Composite={combined_fit_score}% (Decision='{laya_eval.get('overall_decision')}', "
        f"CandSeniority='{laya_eval.get('candidate_seniority_label')}')"
    )

    return {
        "final_score": combined_final_score,
        "fit_score": combined_fit_score,
        "laya_fit_score": laya_fit_score,
        "skill_overlap_percentage": skill_overlap_pct,
        "overall_decision": laya_eval.get("overall_decision", "Moderate match"),
        "seniority_tier": laya_eval.get("candidate_seniority_tier", laya_eval.get("seniority_tier", "mid_level")),
        "seniority_label": laya_eval.get("candidate_seniority_label", laya_eval.get("seniority_label", "Mid-Level")),
        "candidate_seniority_tier": laya_eval.get("candidate_seniority_tier", "mid_level"),
        "candidate_seniority_label": laya_eval.get("candidate_seniority_label", "Mid-Level"),
        "target_seniority_tier": laya_eval.get("target_seniority_tier", "mid_level"),
        "target_seniority_label": laya_eval.get("target_seniority_label", "Mid-Level"),
        "role_weights": laya_eval.get("role_weights", {}),
        "parameter_evaluations": laya_eval.get("parameter_evaluations", {}),
        "raw_weighted_probability": laya_eval.get("raw_weighted_probability", 0.70),
        "high_hits_count": laya_eval.get("high_hits_count", 0),
        "penalty_applied": laya_eval.get("penalty_applied", 0.0),
        "total_weighted_probability": combined_weighted_prob,
        "breakdown": laya_eval.get("breakdown", {}),
        "technical_overlap": {
            "jd_skills_required": jd_skills,
            "matched_skills": matched_skills,
            "missing_jd_skills": missing_jd_skills,
            "candidate_bonus_skills": candidate_bonus,
            "skill_overlap_percentage": overlap_pct,
        },
        "source": "Laya + Skill Overlap 50/50 Scorer",
    }


# Backward-compatible alias
score_resume_against_jd_zero_llm = score_resume_against_jd
