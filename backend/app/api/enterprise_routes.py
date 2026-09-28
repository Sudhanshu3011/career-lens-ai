"""
CareerLens AI - Enterprise Bulk Resume Screening Controller

Thin HTTP controller for batch resume evaluation and Top 3 candidate ranking.
"""

from __future__ import annotations

import json
from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.schemas import (
    EnterpriseBulkScreenResponse,
    JDPreviewRequest,
    JDPreviewResponse,
)
from app.extraction.jd_extractor import preview_job_requirements
from app.services.enterprise_screening_service import screen_resumes_batch
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/enterprise", tags=["Enterprise Screening"])


@router.post(
    "/preview-requirements",
    response_model=JDPreviewResponse,
    summary="Transparent Preview of Extracted JD Criteria, Hard Gates & Evaluation Questions",
    status_code=status.HTTP_200_OK,
)
async def preview_requirements(
    payload: JDPreviewRequest,
) -> JDPreviewResponse:
    """
    Parses and normalizes a Job Description to give recruiters full transparency:
    1. Returns detected technical competencies grouped by category.
    2. Identifies mandatory hard requirement gates.
    3. Provides verbatim previews of the Jev System One questions that will be evaluated.
    Recruiters can inspect, modify, or approve these requirements before running batch screening.
    """
    logger.info(
        f"API Request -> /enterprise/preview-requirements: Role='{payload.job_role}', Pipeline='{payload.pipeline}'"
    )
    result = preview_job_requirements(
        job_description=payload.job_description,
        job_role=payload.job_role,
        pipeline_mode=payload.pipeline,
    )
    return JDPreviewResponse(**result)


@router.post(
    "/bulk-screen",
    response_model=EnterpriseBulkScreenResponse,
    summary="Bulk Screen up to 15 Resumes with Multi-Dimensional Calibration & Rank Top 3",
    status_code=status.HTTP_200_OK,
)
async def bulk_screen_resumes(
    job_role: str = Form(..., min_length=2, description="Target Job Role title, e.g. Senior Backend Engineer"),
    job_description: str = Form(..., min_length=20, description="Full job description requirements"),
    resumes: List[UploadFile] = File(..., description="Up to 15 PDF resumes"),
    pipeline: str = Form("typesafe", description="Decision pipeline: 'typesafe' (TypeSafe Python SDK) or 'laya_local' (Local Laya Router)"),
    approved_requirements: Optional[str] = Form(None, description="Optional JSON array string of recruiter-approved requirements"),
):
    """
    Enterprise batch screening pipeline:
    1. Validates batch size (1 to 15 PDF resumes).
    2. Validates that every file is a valid PDF by extension and MIME type.
    3. Normalizes JD into structured JobProfile (using recruiter-approved criteria if supplied).
    4. Concurrently evaluates and scores candidates via selected pipeline.
    5. Ranks all candidates and flags the Top 3 shortlisted candidates.
    """
    parsed_approved = None
    if approved_requirements:
        try:
            parsed_approved = json.loads(approved_requirements)
            if not isinstance(parsed_approved, list):
                parsed_approved = None
        except Exception as exc:
            logger.warning(f"Failed to parse approved_requirements JSON: {exc}")
            parsed_approved = None

    logger.info(
        f"API Request -> /enterprise/bulk-screen: Target Role='{job_role}', Pipeline='{pipeline}', "
        f"ApprovedRequirements={len(parsed_approved) if parsed_approved else 'auto'}, Batch Size={len(resumes)} file(s)"
    )
    return await screen_resumes_batch(
        job_role=job_role,
        job_description=job_description,
        resumes=resumes,
        pipeline_mode=pipeline,
        approved_requirements=parsed_approved,
    )
