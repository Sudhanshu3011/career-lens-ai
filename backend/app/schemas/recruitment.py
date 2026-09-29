"""
CareerLens AI - Recruitment & Dynamic Evaluation Schemas
Pydantic V2 models for JD question synthesis, recruiter customization,
granular resume details, and throttled candidate evaluation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvaluationQuestionItem(BaseModel):
    """Individual evaluation question representation with primitive and dealbreaker toggle."""
    name: str = Field(..., description="Unique question identifier, e.g. domain_alignment or gate name")
    type: str = Field(..., description="Primitive type: 'choice', 'score', or 'noul'")
    primitive: str = Field(..., description="Canonical TypeSafe/Laya primitive: 'Choice', 'Score', or 'Noul'")
    scale: str = Field(..., description="Scale or options description, e.g. '0.0 to 5.0' or 'P(True) in [0.0, 1.0]'")
    instructions: str = Field(..., description="Exact evaluation question instruction / prompt")
    is_mandatory: bool = Field(False, description="Whether failure of this question causes an immediate candidate veto")
    category: Optional[str] = Field("criteria", description="Question category: gate, domain, seniority, depth, evidence")

    model_config = ConfigDict(extra="allow")


class JobAnalyzeRequest(BaseModel):
    """Request schema for analyzing a Job Description and generating dynamic questions."""
    role_title: str = Field(..., min_length=2, description="Target job role title, e.g. Senior Backend Engineer")
    job_description: str = Field(..., min_length=20, description="Full job description text")


class JobAnalyzeResponse(BaseModel):
    """Response schema returned upon JD analysis and question synthesis."""
    job_id: str
    role_title: str
    jd_hash: str
    is_reviewed: bool
    blueprint: Dict[str, Any]
    questions: Dict[str, EvaluationQuestionItem]
    cached: bool = False
    message: str = "Evaluation blueprint and questions generated successfully."


class JobQuestionsUpdateRequest(BaseModel):
    """Request schema for recruiter question customization and mandatory gate toggles."""
    questions: Dict[str, EvaluationQuestionItem] = Field(
        ..., description="Recruiter-reviewed dictionary of questions with updated prompts or is_mandatory flags"
    )


class JobQuestionsUpdateResponse(BaseModel):
    """Response schema confirming recruiter question review."""
    job_id: str
    is_reviewed: bool
    total_questions: int
    mandatory_gates_count: int
    questions: Dict[str, EvaluationQuestionItem]
    message: str = "Questions successfully reviewed and locked for candidate evaluation."


class ResumeUploadResponseItem(BaseModel):
    """Status summary for an uploaded resume file."""
    resume_id: str
    filename: str
    file_hash: str
    file_size_bytes: int
    status: str = Field(..., description="'cached', 'queued', 'completed', or 'failed'")
    eta_seconds: Optional[int] = Field(None, description="Estimated wait time in seconds if queued")
    message: Optional[str] = None
    error_message: Optional[str] = None


class ResumeUploadBatchResponse(BaseModel):
    """Response schema for multi-file resume upload."""
    total_uploaded: int
    cached_count: int
    queued_count: int
    resumes: List[ResumeUploadResponseItem]


class ResumeDetailResponse(BaseModel):
    """Granular parsed resume details schema exposing all canonical sections."""
    resume_id: str
    filename: str
    file_hash: str
    file_size_bytes: int
    status: str
    parsed_sections: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    portfolio_links: List[str] = []
    error_message: Optional[str] = None


class JobEvaluationRequest(BaseModel):
    """Request schema to trigger candidate evaluation against reviewed questions."""
    resume_ids: List[str] = Field(..., min_length=1, description="List of parsed resume IDs to evaluate")
    pipeline: str = Field("laya", description="Inference pipeline to run: 'laya' or 'jev'")


class CandidateEvaluationItem(BaseModel):
    """Evaluation verdict for an individual candidate."""
    evaluation_id: str
    job_id: str
    resume_id: str
    candidate_name: str
    pipeline: str
    fit_score: float
    verdict: str
    status: str
    breakdown: Dict[str, Any] = {}
    portfolio_links: List[str] = []
    projects: List[Dict[str, Any]] = []
    error_message: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class JobEvaluationSummaryResponse(BaseModel):
    """Response schema for completed evaluation batch."""
    job_id: str
    total_evaluated: int
    top_candidates: List[CandidateEvaluationItem]
    evaluations: List[CandidateEvaluationItem]
