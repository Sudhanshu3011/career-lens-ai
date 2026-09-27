"""
CareerLens AI - ML Prompt Templates & Ground-Truth Anchors

Generates prompts and criteria for the 5-dimension candidate evaluation.
Includes Ground-Truth Anchoring: explicitly injects deterministic skill matches
and deficits into the prompt so Laya's attention mechanism avoids neutral middle-tier bias.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_candidate_prompt(
    job_description: str,
    job_role: str,
    tech_skills: List[str],
    tools: List[str],
    domains: List[str],
    education_text: str,
    experience_text: str,
    technical_overlap: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Assembles the complete, unabbreviated context payload for Laya inference.
    Injects deterministic technical verification as a ground-truth anchor.
    """
    clean_role = (job_role or "").strip()
    role_header = f"Target Position: {clean_role}\n" if clean_role else ""

    # Ground-Truth Verification Section
    verification_section = ""
    if technical_overlap:
        matched = technical_overlap.get("matched_skills", [])
        missing = technical_overlap.get("missing_jd_skills", [])
        overlap_pct = technical_overlap.get("skill_overlap_percentage", 0.0)

        matched_str = ", ".join(matched) if matched else "NONE (0 matched skills)"
        missing_str = ", ".join(missing[:8]) if missing else "None identified"
        if len(missing) > 8:
            missing_str += f" (+{len(missing) - 8} more)"

        verification_section = (
            f"\nObjective Skill Verification:\n"
            f"- Technical Skill Overlap: {overlap_pct:.1f}%\n"
            f"- Verified Matched Skills: {matched_str}\n"
            f"- Critical Missing Requirements: {missing_str}\n"
        )

    clean_exp = experience_text.strip()
    effective_experience = (
        clean_exp
        if clean_exp
        else "None. Candidate has 0 years of professional work experience (student/fresher profile with academic projects only)."
    )

    candidate_skills_str = ", ".join(tech_skills) if tech_skills else "None identified"
    tools_str = ", ".join(tools) if tools else "None"
    domains_str = ", ".join(domains) if domains else "None"

    return (
        f"Candidate Profile Under Review:\n"
        f"- Technical Skills: {candidate_skills_str}\n"
        f"- Tools & Platforms: {tools_str}\n"
        f"- Domains: {domains_str}\n"
        f"- Experience: {effective_experience}\n"
        f"- Education: {education_text or 'None'}\n\n"
        f"Target Job Requisition:\n"
        f"{role_header}"
        f"Requirements:\n{job_description}\n"
        f"{verification_section}"
    )


def build_parameter_questions(job_role: str = "") -> Dict[str, Any]:
    """Generates the 5 multi-dimensional evaluation questions with dynamic role context."""
    clean_role = (job_role or "").strip()
    role_target = (
        f"for the '{clean_role}' position" if clean_role else "for this position"
    )
    role_noun = f"the {clean_role} role" if clean_role else "the target role"
    role_title = f"as a {clean_role}" if clean_role else "for the target role"

    return {
        "technical": {
            "type": "choice",
            "instructions": (
                f"Evaluate how thoroughly the candidate's technical skills, languages, and frameworks "
                f"satisfy the core technical requirements {role_target}."
            ),
            "criteria": {
                "high": f"Matches nearly all or all essential technical skills and frameworks required {role_target}.",
                "mid": f"Matches a substantial portion of skills for {role_noun} but misses some key technologies.",
                "low": f"Matches few or none of the required technical skills for {role_noun}.",
            },
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
                "low": f"Insufficient relevant experience or significant seniority mismatch {role_target}.",
            },
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
                "low": f"Completely unrelated domain with minimal overlap to {role_noun}.",
            },
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
                "low": f"No relevant degree or education credentials mentioned for {role_noun}.",
            },
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
                "low": f"Vague, passive, or unsubstantiated bullet points lacking demonstrable impact {role_title}.",
            },
        },
    }
