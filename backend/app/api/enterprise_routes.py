"""
CareerLens AI - Enterprise Bulk Resume Screening Controller

Thin HTTP controller for batch resume evaluation and Top 3 candidate ranking.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.schemas import EnterpriseBulkScreenResponse
from app.services.enterprise_screening_service import screen_resumes_batch
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/enterprise", tags=["Enterprise Screening"])


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
):
    """
    Enterprise batch screening pipeline:
    1. Validates batch size (1 to 15 PDF resumes).
    2. Validates that every file is a valid PDF by extension and MIME type.
    3. Concurrently evaluates and scores candidates.
    4. Ranks all candidates and flags the Top 3 shortlisted candidates.
    """
    logger.info(
        f"API Request -> /enterprise/bulk-screen: Target Role='{job_role}', Batch Size={len(resumes)} file(s)"
    )
    return await screen_resumes_batch(
        job_role=job_role,
        job_description=job_description,
        resumes=resumes,
    )
