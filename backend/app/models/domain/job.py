"""
CareerLens AI - TypeSafe Job Profile Domain Models
Structured representation of target job requirements decomposed into atomic dimensions.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RequirementItem(BaseModel):
    """An individual atomic requirement extracted from the job description."""

    name: str = Field(
        ..., description="Canonical requirement name (e.g. Python, AWS, Bachelor's)"
    )
    category: str = Field(
        default="skill",
        description="Requirement category: skill, experience, education, domain",
    )
    is_hard_requirement: bool = Field(
        default=False,
        description="Whether this is a mandatory/non-negotiable requirement",
    )
    target_years: Optional[float] = Field(
        default=None, description="Minimum years required if specified"
    )
    description: str = Field(
        default="", description="Original context or explanation from JD"
    )


class JobProfile(BaseModel):
    """Complete structured representation of normalized job description."""

    role_title: str = Field(default="", description="Target position title")
    seniority_score: float = Field(
        default=2.0,
        ge=0.0,
        le=6.0,
        description="Continuous seniority rating on 0-6 rubric",
    )
    seniority_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence of seniority classification",
    )
    seniority_label: str = Field(
        default="Mid-Level", description="Human-readable seniority tier"
    )
    role_family: str = Field(
        default="software_engineering",
        description="Job family from predefined taxonomy",
    )
    domain: str = Field(default="general", description="Primary engineering domain")

    required_skills: List[str] = Field(
        default_factory=list, description="Core technical competencies"
    )
    preferred_skills: List[str] = Field(
        default_factory=list, description="Bonus / nice-to-have skills"
    )
    hard_requirements: List[RequirementItem] = Field(
        default_factory=list, description="Mandatory gate requirements"
    )

    required_experience_years: Optional[float] = Field(
        default=None, description="Explicit minimum years from text"
    )
    education_requirements: List[str] = Field(
        default_factory=list, description="Degree or credential requirements"
    )
    raw_text: str = Field(default="", description="Cleaned original JD text")
