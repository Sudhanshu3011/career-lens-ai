"""
CareerLens AI - Job Requisition & Evaluation Endpoints
REST API for dynamic JD question synthesis, recruiter review, and candidate evaluation.
"""

from __future__ import annotations

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_database_session
from app.schemas.recruitment import (
    JobAnalyzeRequest,
    JobAnalyzeResponse,
    JobEvaluationRequest,
    JobEvaluationSummaryResponse,
    JobQuestionsUpdateRequest,
    JobQuestionsUpdateResponse,
)
from app.services.recruitment_service import recruitment_service

router = APIRouter(prefix="/jobs", tags=["Job Requisitions & Evaluation"])


@router.post(
    "/analyze",
    response_model=JobAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Job Description & Generate Dynamic Questions",
    description=(
        "Analyzes a target Job Description, checks the database for an existing SHA-256 hash, "
        "synthesizes dynamic assessment questions (Choice, Score, Noul), and returns them for recruiter review."
    ),
)
async def analyze_job(
    payload: JobAnalyzeRequest,
    db: Session = Depends(get_database_session),
) -> JobAnalyzeResponse:
    return await recruitment_service.analyze_job_requisition(
        db=db,
        role_title=payload.role_title,
        job_description=payload.job_description,
    )


@router.get(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Job Requisition Details & Questions",
)
def get_job(
    job_id: str,
    db: Session = Depends(get_database_session),
):
    job = recruitment_service.get_job(db=db, job_id=job_id)
    blueprint = json.loads(job.blueprint_json) if job.blueprint_json else {}
    questions = json.loads(job.configured_questions_json) if job.configured_questions_json else {}
    return {
        "job_id": job.id,
        "role_title": job.role_title,
        "jd_hash": job.jd_hash,
        "is_reviewed": job.is_reviewed,
        "blueprint": blueprint,
        "questions": questions,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.put(
    "/{job_id}/questions",
    response_model=JobQuestionsUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Recruiter Question Review & Dealbreaker Customization (Mandatory Gate)",
    description=(
        "Mandatory Precondition Gate: Allows the recruiter to review synthesized questions, "
        "edit wording, and toggle 'is_mandatory' flags for dealbreakers before running candidate evaluation. "
        "Sets 'is_reviewed = True'."
    ),
)
def update_job_questions(
    job_id: str,
    payload: JobQuestionsUpdateRequest,
    db: Session = Depends(get_database_session),
) -> JobQuestionsUpdateResponse:
    return recruitment_service.update_job_questions(
        db=db,
        job_id=job_id,
        questions=payload.questions,
    )


@router.post(
    "/{job_id}/evaluations",
    response_model=JobEvaluationSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Candidates Against Reviewed Questions (Throttled)",
    description=(
        "Evaluates candidates using ConvAI Laya / TypeSafe Jev. "
        "Enforces the 'is_reviewed == True' precondition gate, throttles inference to 2 parallel tasks "
        "to prevent RAM/VRAM exhaustion, and returns final scores and dealbreaker verdicts."
    ),
)
async def evaluate_candidates(
    job_id: str,
    payload: JobEvaluationRequest,
    db: Session = Depends(get_database_session),
) -> JobEvaluationSummaryResponse:
    return await recruitment_service.evaluate_candidates_sync(
        db=db,
        job_id=job_id,
        resume_ids=payload.resume_ids,
        pipeline=payload.pipeline,
    )


@router.post(
    "/{job_id}/evaluations/stream",
    summary="Real-Time Streaming Evaluation (Server-Sent Events)",
    description=(
        "Streams candidate evaluations in real-time as Server-Sent Events (SSE). "
        "Yields an event immediately as each individual candidate finishes inference."
    ),
)
async def stream_candidate_evaluations(
    job_id: str,
    payload: JobEvaluationRequest,
    db: Session = Depends(get_database_session),
):
    stream_generator = recruitment_service.stream_candidate_evaluations(
        db=db,
        job_id=job_id,
        resume_ids=payload.resume_ids,
        pipeline=payload.pipeline,
    )
    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
