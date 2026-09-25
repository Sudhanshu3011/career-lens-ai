"""
CareerLens AI - Analysis Service

Orchestrates deterministic parsing, calibrated Laya candidate evaluation,
and career coaching diagnostics.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List
from fastapi import HTTPException, UploadFile, status

from app.core.logger import get_logger
from app.tools.candidate_scorer import score_resume_against_jd
from app.tools.deterministic_parser import parse_resume_from_pdf
from app.validator.pdf_validator import validate_pdf

logger = get_logger(__name__)


def _extract_parsed_sections(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts raw textual sections from deterministic resume parsing."""
    return {
        "candidate_name": parsed_data.get("candidate_name", "Candidate"),
        "contact_info": parsed_data.get("contact_info", {}),
        "summary": parsed_data.get("summary", ""),
        "experience": parsed_data.get("experience", ""),
        "education": parsed_data.get("education", ""),
        "skills": parsed_data.get("skills", ""),
        "projects": parsed_data.get("projects", ""),
        "certifications": parsed_data.get("certifications", ""),
    }


def _extract_skills_analysis(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Formats candidate technical competencies and taxonomy domain groupings."""
    tech_skills = parsed_data.get("tech_skills", [])
    skills_by_domain = parsed_data.get("skills_by_domain", {})

    tools = (
        skills_by_domain.get("DevOps & Cloud", [])
        + skills_by_domain.get("Big Data & Distributed Computing", [])
    )
    domains = list(skills_by_domain.keys())

    return {
        "technical_skills": tech_skills,
        "tools_and_platforms": tools,
        "domains": domains,
        "skills_by_domain": skills_by_domain,
        "seniority": "Mid-Level",
    }


async def run_full_resume_analysis(
    resume: UploadFile,
    job_description: str,
) -> Dict[str, Any]:
    """
    Executes end-to-end resume evaluation against target job requirements.
    Runs asynchronous non-blocking IO and offloads CPU-bound parsing/scoring.
    """
    pdf_bytes = await resume.read()
    validate_pdf(resume, pdf_bytes)

    logger.info(
        f"Processing resume analysis: {resume.filename} "
        f"({len(pdf_bytes) / (1024 * 1024):.2f} MB)"
    )

    try:
        # 1. Deterministic document parsing in thread
        parsed_data = await asyncio.to_thread(parse_resume_from_pdf, pdf_bytes)
        parsed_sections = _extract_parsed_sections(parsed_data)
        skills_analysis = _extract_skills_analysis(parsed_data)

        # 2. Seniority-weighted Laya scoring in thread
        scoring_res = await asyncio.to_thread(
            score_resume_against_jd,
            resume_data=parsed_data,
            job_description=job_description.strip(),
        )

        breakdown = scoring_res.get("breakdown", {})

        final_response = {
            "parsed_resume": parsed_sections,
            "skills_analysis": skills_analysis,
            "decision_breakdown": breakdown,
            "scores": scoring_res,
            "seniority_tier": scoring_res.get("seniority_tier", "mid_level"),
            "seniority_label": scoring_res.get("seniority_label", "Mid-Level"),
            "role_weights": scoring_res.get("role_weights", {}),
            "high_hits_count": scoring_res.get("high_hits_count", 0),
            "feedback": [],
            "strengths": [],
            "growth_areas": [],
            "actionable_steps": [],
            "elevation_roadmap": {},
            "recommended_jobs": [],
            "best_job_recommendation": None,
        }

        return {"success": True, "data": final_response}

    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Resume analysis pipeline encountered an unexpected error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume analysis failed: {str(err)}",
        )


