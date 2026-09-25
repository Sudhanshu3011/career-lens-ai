"""
CareerLens AI - Core Enterprise & Health Controller

Controller for system health verification and single-resume deterministic analysis.
"""

from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.schemas import ResumeAnalysisResponse
from app.services.analysis_service import run_full_resume_analysis

router = APIRouter(tags=["Analysis"])


@router.get("/health", summary="Health check")
async def health_check():
    """System health check and pipeline status."""
    return {
        "status": "healthy",
        "service": "careerlens-enterprise",
        "version": "1.0.0",
        "pipeline": "deterministic-calibrated-laya",
    }


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    summary="Analyze a resume PDF with calibrated multi-dimensional scoring",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def analyze_resume(
    resume: UploadFile = File(..., description="PDF resume file (max 5 MB)"),
    job_description: str = Form(
        ...,
        min_length=20,
        max_length=15000,
        description="Complete job description text for candidate matching.",
    ),
):
    """Upload a PDF resume and job description to receive structured analysis."""
    return await run_full_resume_analysis(resume=resume, job_description=job_description)
