"""
CareerLens AI - Resume Management & Granular Detail Endpoints
REST API for resume ingestion, deduplication, and granular 6-section parsed data access.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database_session
from app.schemas.recruitment import (
    ResumeDetailResponse,
    ResumeUploadBatchResponse,
    ResumeUploadResponseItem,
)
from app.services.recruitment_service import recruitment_service

router = APIRouter(prefix="/resumes", tags=["Resumes & Parsing"])


@router.post(
    "/upload",
    response_model=ResumeUploadBatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload & Parse Resumes (Rate-Limited 1 req/min with Deduplication)",
    description=(
        "Uploads 1 to 15 PDF resumes. Calculates SHA-256 byte hashes for instant deduplication. "
        "Cached resumes return immediately with 0s latency. "
        "New resumes are enqueued for sequential 1 req/min LLM parsing."
    ),
)
async def upload_resumes(
    files: List[UploadFile] = File(..., description="1 to 15 PDF resume files"),
    db: Session = Depends(get_database_session),
) -> ResumeUploadBatchResponse:
    if len(files) > 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum batch limit is 15 resumes per request.",
        )
    for f in files:
        if f.filename and not f.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only PDF files are supported. Invalid file: '{f.filename}'",
            )

    return await recruitment_service.upload_resumes(db=db, files=files)


@router.get(
    "/{resume_id}",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Granular Parsed Resume Details (6 Canonical Sections)",
    description=(
        "Returns the complete parsed details of a candidate resume, including contact info, "
        "professional summary, chronological work experience timeline, core competencies, "
        "education credentials, certifications/licenses, and raw text."
    ),
)
def get_resume_detail(
    resume_id: str,
    db: Session = Depends(get_database_session),
) -> ResumeDetailResponse:
    return recruitment_service.get_resume_detail(db=db, resume_id=resume_id)


@router.post(
    "/{resume_id}/reparse",
    response_model=ResumeUploadResponseItem,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-parse Resume with High-Precision LLM",
    description=(
        "Retries structured parsing for a candidate resume that encountered disruption, "
        "rate-limiting, or produced incomplete data. Never persists incomplete data to database."
    ),
)
async def reparse_resume(
    resume_id: str,
    db: Session = Depends(get_database_session),
) -> ResumeUploadResponseItem:
    return await recruitment_service.reparse_resume(db=db, resume_id=resume_id)

