"""
CareerLens AI - Structured Job Description Normalizer
Extracts technical competencies, explicit criteria, and Jev semantic properties into JobProfile.
"""

from __future__ import annotations

import re
from typing import List, Optional, Dict, Any
from app.models.domain.job import JobProfile, RequirementItem
from app.engines.extraction.tech_keywords import extract_tech_keywords
from app.engines.jev.client import jev_client
from app.engines.laya.client import laya_client
from app.engines.jev.questions import build_jd_questions
from app.engines.jev.rubric import seniority_score_to_label
from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_job_profile(
    job_description: str,
    job_role: str = "",
    pipeline_mode: str = "typesafe",
    approved_requirements: Optional[List[Dict[str, Any]]] = None,
) -> JobProfile:
    """
    Parses and normalizes a Job Description into a structured JobProfile:
    1. Extracts technical competencies via 450+ IT skill taxonomy (or uses approved requirements).
    2. Identifies mandatory/hard qualifications.
    3. Executes Stage 1 Jev call (JD Seniority Score, Role Family Choice, Domain Choice).
    """
    clean_jd = (job_description or "").strip()
    clean_role = (job_role or "").strip()
    combined_text = (
        f"Target Position: {clean_role}\n\nJob Description:\n{clean_jd}"
        if clean_role
        else clean_jd
    )

    # 1. Deterministic technical skills extraction
    tech_data = extract_tech_keywords(combined_text)
    extracted_skills: List[str] = tech_data.get("extracted_skills", [])

    # 2. Extract explicit required years of experience
    years_matches = [
        int(y)
        for y in re.findall(r"(\d+)\+?\s*(?:years|yrs)", combined_text.lower())
        if int(y) < 30
    ]
    required_years: Optional[float] = (
        float(max(years_matches)) if years_matches else None
    )

    # 3. Handle recruiter-approved requirements OR auto-detect hard requirements
    hard_requirements: List[RequirementItem] = []
    if approved_requirements:
        user_skills: List[str] = []
        for item in approved_requirements:
            name = item.get("name", "").strip()
            if not name:
                continue
            is_hard = bool(item.get("is_hard_requirement", False))
            cat = item.get("category", "skill")
            user_skills.append(name)
            if is_hard:
                hard_requirements.append(
                    RequirementItem(
                        name=name,
                        category=cat,
                        is_hard_requirement=True,
                        target_years=required_years,
                        description=f"Recruiter-approved mandatory requirement: {name}",
                    )
                )
        if user_skills:
            extracted_skills = user_skills
    else:
        lines = clean_jd.splitlines()
        must_have_cues = [
            "must have",
            "required",
            "mandatory",
            "minimum",
            "essential",
            "qualification",
        ]

        for skill in extracted_skills:
            is_hard = False
            for l in lines:
                l_lower = l.lower()
                if skill.lower() in l_lower and any(
                    cue in l_lower for cue in must_have_cues
                ):
                    is_hard = True
                    break
            if is_hard:
                hard_requirements.append(
                    RequirementItem(
                        name=skill,
                        category="skill",
                        is_hard_requirement=True,
                        target_years=required_years,
                        description=f"Mandatory requirement: {skill}",
                    )
                )

        # If no explicit hard requirements identified, select top 2-3 core skills
        if not hard_requirements and extracted_skills:
            for s in extracted_skills[:3]:
                hard_requirements.append(
                    RequirementItem(
                        name=s,
                        category="skill",
                        is_hard_requirement=True,
                        description=f"Core required skill: {s}",
                    )
                )

    # 4. Stage 1 Call: Evaluate Seniority, Role Family, and Domain simultaneously
    questions = build_jd_questions(role_title=clean_role)
    client = laya_client if pipeline_mode == "laya_local" else jev_client
    answers = client.predict(state={"text": combined_text}, questions=questions)

    sen_ans = answers.get("jd_seniority", {})
    seniority_score = float(sen_ans.get("score", 2.0))
    seniority_conf = float(sen_ans.get("confidence", 0.70))
    seniority_label = seniority_score_to_label(seniority_score)

    rf_ans = answers.get("role_family", {})
    role_family = str(rf_ans.get("choice", "backend"))

    dom_ans = answers.get("domain", {})
    domain = str(dom_ans.get("choice", "web_cloud"))

    logger.info(
        f"Normalized JD: Role='{clean_role or role_family}', SeniorityScore={seniority_score:.2f} "
        f"({seniority_label}), Domain='{domain}', Skills={len(extracted_skills)}, "
        f"HardGates={len(hard_requirements)}"
    )

    return JobProfile(
        role_title=clean_role or role_family.replace("_", " ").title(),
        seniority_score=round(seniority_score, 2),
        seniority_confidence=round(seniority_conf, 2),
        seniority_label=seniority_label,
        role_family=role_family,
        domain=domain,
        required_skills=extracted_skills,
        preferred_skills=[],
        hard_requirements=hard_requirements,
        required_experience_years=required_years,
        education_requirements=[],
        raw_text=clean_jd,
    )


def preview_job_requirements(
    job_description: str,
    job_role: str = "",
    pipeline_mode: str = "typesafe",
) -> Dict[str, Any]:
    """
    Transparent preview of extracted requirements and suggested evaluation questions for recruiter approval.
    """
    job_profile = extract_job_profile(
        job_description=job_description,
        job_role=job_role,
        pipeline_mode=pipeline_mode,
    )

    clean_jd = (job_description or "").strip()
    clean_role = (job_role or "").strip()
    combined_text = (
        f"Target Position: {clean_role}\n\nJob Description:\n{clean_jd}"
        if clean_role
        else clean_jd
    )
    tech_data = extract_tech_keywords(combined_text)
    skills_by_domain = tech_data.get("skills_by_domain", {})

    hard_req_names = {r.name.lower() for r in job_profile.hard_requirements}
    all_skills = list(
        dict.fromkeys(
            [r.name for r in job_profile.hard_requirements]
            + job_profile.required_skills
        )
    )

    suggested_requirements: List[Dict[str, Any]] = []
    for skill in all_skills:
        is_hard = skill.lower() in hard_req_names
        cat = "skill"
        for d, s_list in skills_by_domain.items():
            if any(s.lower() == skill.lower() for s in s_list):
                cat = d
                break

        suggested_requirements.append(
            {
                "name": skill,
                "category": cat,
                "is_hard_requirement": is_hard,
                "target_years": job_profile.required_experience_years,
                "description": (
                    f"Mandatory gate requirement: {skill}"
                    if is_hard
                    else f"Evaluated competency: {skill}"
                ),
                "suggested_gate_question": f"Does candidate provide verified evidence satisfying '{skill}'?",
                "suggested_direct_question": f"Is there direct production or project execution evidence using '{skill}'?",
                "suggested_strength_question": f"Rate depth and strength of competency in '{skill}' (0-5).",
            }
        )

    preview_questions_summary = {
        "candidate_seniority_question": "Evaluates candidate career seniority on continuous 0.0 to 6.0 scale.",
        "evaluated_requirements_count": len(suggested_requirements),
        "hard_gates_count": len(job_profile.hard_requirements),
    }

    return {
        "success": True,
        "job_role": job_profile.role_title,
        "seniority_score": job_profile.seniority_score,
        "seniority_label": job_profile.seniority_label,
        "role_family": job_profile.role_family,
        "domain": job_profile.domain,
        "total_detected_skills": len(all_skills),
        "detected_skills_by_category": skills_by_domain,
        "suggested_requirements": suggested_requirements,
        "preview_questions_summary": preview_questions_summary,
    }
