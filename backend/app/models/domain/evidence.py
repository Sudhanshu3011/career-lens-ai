"""
CareerLens AI - TypeSafe Evidence & Assessment Domain Models
Atomic evidence items traceable back to resume blocks and multi-factor assessments.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A concrete textual snippet from the resume supporting a capability or credential."""

    evidence_id: str = Field(..., description="Unique evidence identifier, e.g. E101")
    source_block_id: str = Field(
        ..., description="Foreign key to source ResumeBlock id"
    )
    section: str = Field(
        default="experience",
        description="Originating section (experience, projects, etc.)",
    )
    text: str = Field(..., description="Exact snippet text from resume")
    skills_mentioned: List[str] = Field(
        default_factory=list, description="Skills detected in this snippet"
    )


class EvidenceAssessment(BaseModel):
    """Decomposed multi-dimensional evaluation of candidate evidence against a JD requirement."""

    requirement_name: str = Field(..., description="Target requirement evaluated")
    is_hard_requirement: bool = Field(
        default=False, description="Whether requirement is mandatory"
    )

    # Primitives outputs
    satisfied_probability: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Noul P(satisfied)"
    )
    direct_evidence_probability: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Noul P(direct evidence exists)"
    )
    evidence_strength: float = Field(
        default=0.0, ge=0.0, le=5.0, description="Score (0-5) depth of evidence"
    )
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=5.0, description="Score (0-5) relevance to requirement"
    )

    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Judgment confidence"
    )
    verdict: str = Field(
        default="missing",
        description="satisfied, partially_satisfied, missing, uncertain",
    )
    evidence_snippets: List[str] = Field(
        default_factory=list, description="Associated source evidence text"
    )
