"""
CareerLens AI - Session & Showcase Screening Schemas
Pydantic V2 models for step-by-step session lifecycle and candidate showcase screening.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CandidateScreeningItem(BaseModel):
    id: str
    name: str
    title: str
    fit_score: int
    decision: str
    rank: int
    is_top_3: bool
    is_top_5: bool
    skills: List[str]
    missing_skills: List[str]
    explanation: str

    model_config = ConfigDict(extra="allow")


class CandidateScreeningInput(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    title: Optional[str] = ""
    skills: List[str] = Field(default_factory=list)
    experience_text: Optional[str] = ""
    education: Optional[str] = ""
    summary: Optional[str] = ""

    model_config = ConfigDict(extra="allow")


class BatchScreeningRequest(BaseModel):
    job_description: str
    candidates: List[CandidateScreeningInput] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class CandidateScreeningResponse(BaseModel):
    success: bool = True
    total_candidates: int
    top_3_count: int
    top_5_count: int
    selected_count: int
    candidates: List[CandidateScreeningItem]


class SessionSummarySchema(BaseModel):
    session_id: str
    status: str
    current_step: int
    resume_filename: str
    created_at: str
    message: Optional[str] = None

    model_config = ConfigDict(extra="allow")
