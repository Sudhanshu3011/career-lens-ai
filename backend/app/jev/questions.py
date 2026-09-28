"""
CareerLens AI - TypeSafe Jev Question Builders
Constructs standard Choice, Score, and Noul questions mapped to versioned rubrics.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List
from app.jev.rubric import RESUME_RUBRIC_V1


def clean_question_id(name: str) -> str:
    """Generates a valid identifier for question keys."""
    clean = re.sub(r"[^a-zA-Z0-9_]+", "_", name.lower().strip())
    return clean[:40].strip("_")


def build_jd_questions(role_title: str = "") -> Dict[str, Any]:
    """
    Builds Stage 1 parallel questions for analyzing a Job Description in 1 Jev call:
    - JD Seniority: Score (0.0 to 6.0)
    - Role Family: Choice
    - Domain: Choice
    """
    role_clause = f" for the target role '{role_title}'" if role_title else ""
    return {
        "jd_seniority": {
            "type": "score",
            "instructions": (
                f"Determine the expected candidate seniority demanded{role_clause} "
                "based on required years of experience, leadership scope, and technical responsibilities."
            ),
            "criteria": RESUME_RUBRIC_V1["seniority_levels"],
        },
        "role_family": {
            "type": "choice",
            "instructions": (
                f"Identify the primary software engineering role family{role_clause}."
            ),
            "criteria": RESUME_RUBRIC_V1["role_families"],
        },
        "domain": {
            "type": "choice",
            "instructions": (
                f"Select the primary technical or industry domain demanded by the job requirements."
            ),
            "criteria": RESUME_RUBRIC_V1["domain_taxonomy"],
        },
    }


def build_candidate_seniority_question() -> Dict[str, Any]:
    """Builds Stage 3 question evaluating candidate's career seniority on continuous 0-6 scale."""
    return {
        "candidate_seniority": {
            "type": "score",
            "instructions": (
                "Determine the candidate's actual personal career seniority based on verified work history, "
                "job titles, project scale, and years of professional execution."
            ),
            "criteria": RESUME_RUBRIC_V1["seniority_levels"],
        }
    }


def build_requirement_questions(requirements: List[str]) -> Dict[str, Any]:
    """
    Builds Stage 4 parallel questions for candidate evidence evaluation against JD requirements:
    - requirement_satisfied: Noul
    - direct_evidence: Noul
    - evidence_strength: Score (0-5)
    All evaluated in a single parallel Jev call per candidate.
    """
    questions: Dict[str, Any] = {}
    for req in requirements:
        safe_id = clean_question_id(req)
        if not safe_id:
            continue

        questions[f"gate_{safe_id}"] = {
            "type": "noul",
            "instructions": (
                f"Does the candidate's resume provide sufficient practical evidence "
                f"that they satisfy the requirement for '{req}'?"
            ),
            "criteria": {
                "false": f"No, the candidate lacks practical evidence or depth in {req}.",
                "true": f"Yes, the candidate provides sufficient verified evidence in {req}."
            }
        }

        questions[f"direct_{safe_id}"] = {
            "type": "noul",
            "instructions": (
                f"Does the candidate present direct professional work or production evidence "
                f"of using '{req}' (as opposed to mere keyword mention)?"
            ),
        }

        questions[f"strength_{safe_id}"] = {
            "type": "score",
            "instructions": (
                f"Rate the depth and strength of candidate's competency in '{req}'."
            ),
            "criteria": RESUME_RUBRIC_V1["skill_strength_levels"],
        }

    return questions


def build_section_classifier_question() -> Dict[str, Any]:
    """Builds Stage 2 Choice question to classify an ambiguous resume block into a canonical section."""
    return {
        "section": {
            "type": "choice",
            "instructions": "Determine which resume section this text block belongs to.",
            "criteria": RESUME_RUBRIC_V1["section_labels"],
        }
    }
