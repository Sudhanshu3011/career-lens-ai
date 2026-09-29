"""
CareerLens AI - Enterprise Bulk Resume Screening Endpoints
Provides endpoints for transparent JD requirement preview and concurrent bulk resume screening.
"""

from __future__ import annotations

import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, status

from app.schemas.enterprise import (
    EnterpriseBulkScreenResponse,
    JDPreviewRequest,
    JDPreviewResponse,
)
from app.engines.extraction.jd_extractor import preview_job_requirements
from app.services.enterprise_service import screen_resumes_batch
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
    result = await asyncio.to_thread(
        preview_job_requirements,
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
    job_role: str = Form(
        ...,
        min_length=2,
        description="Target Job Role title, e.g. Senior Backend Engineer",
    ),
    job_description: str = Form(
        ..., min_length=20, description="Full job description requirements text"
    ),
    pipeline: str = Form(
        "typesafe",
        description="Target evaluation pipeline: 'typesafe' (System One SDK) or 'laya_local' (Edge inference)",
    ),
    approved_requirements_json: Optional[str] = Form(
        None,
        description="Optional JSON-encoded list of approved requirements from preview-requirements endpoint",
    ),
    resumes: List[UploadFile] = File(
        ...,
        description="Up to 15 PDF candidate resume files to screen concurrently",
    ),
) -> EnterpriseBulkScreenResponse:
    """
    Enterprise batch screening endpoint. Evaluates up to 15 resumes concurrently
    against normalized Job Description criteria using TypeSafe System One primitives.
    """
    logger.info(
        f"API Request -> /enterprise/bulk-screen: Role='{job_role}', "
        f"Pipeline='{pipeline}', ResumesCount={len(resumes)}"
    )

    # Parse approved requirements if provided
    approved_reqs = None
    if approved_requirements_json and approved_requirements_json.strip():
        try:
            approved_reqs = json.loads(approved_requirements_json)
        except Exception as e:
            logger.warning(
                f"Failed to parse approved_requirements_json: {e}. Proceeding with fresh extraction."
            )

    result = await screen_resumes_batch(
        job_role=job_role,
        job_description=job_description,
        resumes=resumes,
        pipeline_mode=pipeline,
        approved_requirements=approved_reqs,
    )
    return EnterpriseBulkScreenResponse(**result)
