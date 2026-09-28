"""
CareerLens AI - TypeSafe Candidate Profile Models
Deterministic layout blocks, structured candidate profile, and evidence mappings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResumeBlock(BaseModel):
    """A discrete spatial text block extracted from resume PDF with layout metadata."""
    id: str = Field(..., description="Unique block ID, e.g. b1, b2")
    page: int = Field(default=1, description="1-indexed page number")
    text: str = Field(..., description="Raw text content of the block")
    font_size: float = Field(default=10.0, description="Average or dominant font size")
    is_bold: bool = Field(default=False, description="Whether block is bold/emphasized")
    y_pos: float = Field(default=0.0, description="Vertical position on page")
    section_candidate: str = Field(default="other", description="Heuristic initial section tag")
    section_assigned: Optional[str] = Field(default=None, description="Final assigned section from Jev/rules")


class CandidateProfile(BaseModel):
    """Complete structured candidate representation assembled from blocks and entities."""
    candidate_name: str = Field(default="Candidate", description="Extracted candidate name")
    email: Optional[str] = Field(default=None, description="Extracted email address")
    phone: Optional[str] = Field(default=None, description="Extracted phone number")
    hyperlinks: List[str] = Field(default_factory=list, description="Extracted URLs (LinkedIn, GitHub, etc.)")
    
    seniority_score: float = Field(default=1.0, ge=0.0, le=6.0, description="Continuous seniority rating on 0-6 rubric")
    seniority_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence of seniority classification")
    seniority_label: str = Field(default="Junior / Entry-Level", description="Human-readable career tier")
    
    blocks: List[ResumeBlock] = Field(default_factory=list, description="All parsed layout blocks")
    sections: Dict[str, str] = Field(default_factory=dict, description="Aggregated text per section")
    
    technical_skills: List[str] = Field(default_factory=list, description="Extracted canonical technical skills")
    tools: List[str] = Field(default_factory=list, description="DevOps, cloud, database tools")
    domains: List[str] = Field(default_factory=list, description="Identified technical domains")
    
    experience_years_span: float = Field(default=0.0, description="Estimated calendar years from history")
    summary_text: str = Field(default="", description="Summary or objective section text")
    experience_text: str = Field(default="", description="Work experience section text")
    education_text: str = Field(default="", description="Education section text")
    raw_text: str = Field(default="", description="Full extracted text")
