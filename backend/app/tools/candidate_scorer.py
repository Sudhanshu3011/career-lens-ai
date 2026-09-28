"""
CareerLens AI - Candidate vs. Job Description Scorer

Evaluates candidate competencies against target job requirements using
deterministic technical keyword taxonomy and modular scoring rules.
Independent of legacy decision_engine.py.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from app.tools.tech_keyword_extractor import extract_tech_keywords, expand_with_parent_domains
from app.core.logger import get_logger

logger = get_logger(__name__)

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


def score_resume_against_jd(
    resume_data: Dict[str, Any],
    job_description: str,
    job_role: str = "",
) -> Dict[str, Any]:
    """
    Evaluates candidate resume against target job description.
    Uses deterministic 450+ IT skill ontology, dynamic role weights,
    and modular parameter scoring.
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
    jd_skills_raw: List[str] = jd_analysis.get("extracted_skills", [])
    # Expand JD skills with umbrella terms so sub-fields count toward broader categories
    jd_skills: List[str] = expand_with_parent_domains(jd_skills_raw)

    # 2. Extract or retrieve candidate skills
    cand_skills_raw: List[str] = resume_data.get("tech_skills", [])
    if not cand_skills_raw and "raw_text" in resume_data:
        cand_analysis = extract_tech_keywords(resume_data["raw_text"])
        cand_skills_raw = cand_analysis.get("extracted_skills", [])
    # Expand candidate skills with umbrella terms (e.g. PyTorch → Machine Learning)
    cand_skills: List[str] = expand_with_parent_domains(cand_skills_raw)

    # 3. Compute deterministic technical overlap (using expanded skill sets)
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

    # ── HARD GATE: < 20% technical overlap → immediate REJECT ────────────────
    # Return a minimal payload. No per-rubric breakdown is shown to avoid
    # misleading partially-matching scores for fundamentally wrong profiles.
    if overlap_pct < 20.0:
        logger.info(
            "Candidate hard-rejected (technical gate): overlap=%.1f%%  matched=%s",
            overlap_pct,
            matched_skills,
        )
        return {
            "final_score": 0.0,
            "fit_score": 0.0,
            "laya_fit_score": 0.0,
            "skill_overlap_percentage": overlap_pct,
            "overall_decision": "REJECT",
            "rejection_reason": "does_not_fit_role",
            "rejection_message": (
                f"Candidate's technical skills ({round(overlap_pct, 1)}% overlap) "
                f"do not meet the minimum threshold for this role. "
                f"Matched: {matched_skills or ['none']}. "
                f"Required but missing: {missing_jd_skills[:6]}."
            ),
            "seniority_tier": "mid_level",
            "seniority_label": "Mid-Level",
            "candidate_seniority_tier": "mid_level",
            "candidate_seniority_label": "Mid-Level",
            "target_seniority_tier": "mid_level",
            "target_seniority_label": "Mid-Level",
            "role_weights": {},
            "parameter_evaluations": {},
            "raw_weighted_probability": 0.0,
            "high_hits_count": 0,
            "penalty_applied": 0.0,
            "total_weighted_probability": 0.0,
            "breakdown": {
                "technical_requirements": round(overlap_pct, 1),
                "experience_requirements": 0,
                "domain_alignment": 0,
                "education_alignment": 0,
                "evidence_strength": 0,
            },
            "technical_overlap": {
                "jd_skills_required": jd_skills_raw,
                "matched_skills": matched_skills,
                "missing_jd_skills": missing_jd_skills,
                "candidate_bonus_skills": candidate_bonus,
                "skill_overlap_percentage": overlap_pct,
            },
            "source": "Hard Technical Gate",
        }

    # 4. Determine Target JD Seniority Tier
    jd_text_lower = f"{job_role} {job_description}".lower()
    if any(w in jd_text_lower for w in ["staff", "principal", "architect", "lead", "senior", "sr.", "8+", "7+", "6+", "5+ years", "5+ yrs"]):
        target_seniority = "senior"
    elif any(w in jd_text_lower for w in ["intern", "graduate", "entry", "fresher", "junior", "0-1", "0-2"]):
        target_seniority = "beginner"
    else:
        target_seniority = "mid_level"

    target_label = SENIORITY_LABELS[target_seniority]
    weights = ROLE_WEIGHTS[target_seniority]

    # 5. Determine Candidate Seniority Tier
    experience_text = (
        resume_data.get("experience", "")
        or resume_data.get("summary", "")
        or resume_data.get("raw_text", "")
    )
    exp_lower = experience_text.lower()
    years_found = [int(y) for y in re.findall(r"(\d+)\+?\s*(?:years|yrs)", exp_lower) if int(y) < 30]
    max_years = max(years_found) if years_found else 2

    if max_years >= 5 or any(w in exp_lower for w in ["lead", "staff", "principal", "senior", "sr."]):
        cand_seniority = "senior"
    elif max_years <= 1 or any(w in exp_lower for w in ["intern", "student", "entry"]):
        cand_seniority = "beginner"
    else:
        cand_seniority = "mid_level"

    cand_label = SENIORITY_LABELS[cand_seniority]

    # 6. Parameter evaluations (0.0 to 1.0)
    p_tech = min(1.0, overlap_pct / 100.0)
    p_exp = min(1.0, 0.40 + (max_years / 10.0) * 0.60)
    
    # Domain match
    domains = resume_data.get("domains") or list(resume_data.get("skills_by_domain", {}).keys())
    p_dom = 0.85 if len(domains) > 0 else 0.50

    # Education match
    education_text = resume_data.get("education", "") or ""
    p_edu = 0.90 if any(d in education_text.lower() for d in ["bachelor", "master", "phd", "b.tech", "degree", "bs", "ms"]) else 0.60

    # Evidence strength
    metrics_count = len(re.findall(r"\d+%", exp_lower)) + len(re.findall(r"\$\d+", exp_lower))
    p_evi = min(1.0, 0.60 + metrics_count * 0.10)

    parameter_evaluations = {}
    probs = {"technical": p_tech, "experience": p_exp, "domain": p_dom, "education": p_edu, "evidence": p_evi}
    high_hits = 0

    for param, p_val in probs.items():
        is_high = p_val >= 0.70
        if is_high:
            high_hits += 1
        w_val = weights.get(param, 0.20)
        parameter_evaluations[param] = {
            "p_high": round(p_val if is_high else 0.20, 3),
            "p_mid": round(p_val if not is_high else 0.50, 3),
            "p_low": round(1.0 - p_val, 3),
            "selected_prob": round(p_val, 3),
            "weight": w_val,
            "weighted_score": round(p_val * w_val, 4),
            "is_high_hit": is_high,
        }

    raw_weighted_prob = sum(p["weighted_score"] for p in parameter_evaluations.values())
    raw_weighted_prob = max(0.0, min(1.0, raw_weighted_prob))

    # Least high hits penalty: max(0.0, (3 - high_hits) * 0.02)
    penalty = max(0.0, (3 - high_hits) * 0.02)
    total_weighted_prob = max(0.0, min(1.0, raw_weighted_prob - penalty))

    fit_score = round(total_weighted_prob * 100.0, 1)

    # 50/50 combination with technical overlap
    combined_fit_score = round(0.50 * fit_score + 0.50 * overlap_pct, 1)
    combined_final_score = round(combined_fit_score / 10.0, 2)
    combined_weighted_prob = round(combined_fit_score / 100.0, 4)

    overall_decision = "SELECT" if combined_fit_score >= 70.0 else ("CONSIDER" if combined_fit_score >= 50.0 else "REJECT")

    breakdown = {
        "technical_requirements": round(p_tech * 100, 1),
        "experience_requirements": round(p_exp * 100, 1),
        "domain_alignment": round(p_dom * 100, 1),
        "education_alignment": round(p_edu * 100, 1),
        "evidence_strength": round(p_evi * 100, 1),
    }

    return {
        "final_score": combined_final_score,
        "fit_score": combined_fit_score,
        "laya_fit_score": fit_score,
        "skill_overlap_percentage": overlap_pct,
        "overall_decision": overall_decision,
        "seniority_tier": cand_seniority,
        "seniority_label": cand_label,
        "candidate_seniority_tier": cand_seniority,
        "candidate_seniority_label": cand_label,
        "target_seniority_tier": target_seniority,
        "target_seniority_label": target_label,
        "role_weights": weights,
        "parameter_evaluations": parameter_evaluations,
        "raw_weighted_probability": round(raw_weighted_prob, 4),
        "high_hits_count": high_hits,
        "penalty_applied": penalty,
        "total_weighted_probability": combined_weighted_prob,
        "breakdown": breakdown,
        "technical_overlap": {
            "jd_skills_required": jd_skills,
            "matched_skills": matched_skills,
            "missing_jd_skills": missing_jd_skills,
            "candidate_bonus_skills": candidate_bonus,
            "skill_overlap_percentage": overlap_pct,
        },
        "source": "Modular Scorer",
    }


score_resume_against_jd_zero_llm = score_resume_against_jd
