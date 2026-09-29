"""
CareerLens AI - Step-by-Step Analysis Sessions Endpoints
Thin HTTP controller managing sequential session execution, persistence,
and real-time candidate showcase screening.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.session_service import SessionService
from app.core.validators import validate_pdf
from app.schemas.session import BatchScreeningRequest

router = APIRouter(prefix="/sessions", tags=["Step-by-Step Analysis Sessions"])


@router.post("", status_code=201)
async def create_session(
    file: UploadFile = File(..., description="PDF Resume file"),
    job_description: str = Form(..., description="Target Job Description text"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new analysis session by uploading a resume PDF and job description."""
    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 50 characters long.",
        )

    pdf_bytes = await file.read()
    validate_pdf(file, pdf_bytes)

    session = SessionService.create_session(
        db=db,
        file_bytes=pdf_bytes,
        filename=file.filename or "resume.pdf",
        job_description=job_description,
    )

    return {
        "session_id": session.id,
        "status": session.status,
        "current_step": session.current_step,
        "resume_filename": session.resume_filename,
        "created_at": session.created_at.isoformat(),
        "message": "Session created successfully. Ready for Step 1 (Parse).",
    }


@router.get("")
def list_sessions(
    limit: int = 20, db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List recent analysis sessions."""
    sessions = SessionService.list_sessions(db=db, limit=limit)
    return [
        {
            "session_id": s.id,
            "status": s.status,
            "current_step": s.current_step,
            "resume_filename": s.resume_filename,
            "created_at": s.created_at.isoformat(),
            "has_decision": bool(s.laya_decision_json),
        }
        for s in sessions
    ]


@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve full analysis session state with all intermediate outputs."""
    session = SessionService.get_session(db=db, session_id=session_id)
    return {
        "session_id": session.id,
        "status": session.status,
        "current_step": session.current_step,
        "resume_filename": session.resume_filename,
        "job_description": session.job_description,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        "error_message": session.error_message,
        "steps_data": {
            "parsed_sections": (
                json.loads(session.parsed_sections_json)
                if session.parsed_sections_json
                else None
            ),
            "skills_data": (
                json.loads(session.skills_data_json)
                if session.skills_data_json
                else None
            ),
            "laya_decision": (
                json.loads(session.laya_decision_json)
                if session.laya_decision_json
                else None
            ),
            "feedback_data": (
                json.loads(session.feedback_json) if session.feedback_json else None
            ),
            "jobs_data": json.loads(session.jobs_json) if session.jobs_json else None,
        },
    }


@router.post("/{session_id}/steps/parse")
def step_1_parse(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute Step 1: Parse resume document structure and sections."""
    parsed = SessionService.execute_step_1_parse(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "step": 1,
        "step_name": "Document Parsing",
        "status": "completed",
        "data": parsed,
    }


@router.post("/{session_id}/steps/skills")
def step_2_skills(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute Step 2: Extract technical skills, soft skills, and competency match."""
    skills = SessionService.execute_step_2_skills(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "step": 2,
        "step_name": "Skill Extraction",
        "status": "completed",
        "data": skills,
    }


@router.post("/{session_id}/steps/decision")
def step_3_decision(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute Step 3: Run Decision Engine & Selection Matrix."""
    decision = SessionService.execute_step_3_decision(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "step": 3,
        "step_name": "Decision & Selection Matrix",
        "status": "completed",
        "data": decision,
    }


@router.post("/{session_id}/steps/feedback")
def step_4_feedback(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute Step 4: Generate targeted diagnostic gaps and coaching feedback."""
    feedback = SessionService.execute_step_4_feedback(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "step": 4,
        "step_name": "Diagnostics & Feedback",
        "status": "completed",
        "data": feedback,
    }


@router.post("/{session_id}/steps/jobs")
def step_5_jobs(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute Step 5: Market Opportunity Matcher with 'Should I Apply?' ranking."""
    jobs = SessionService.execute_step_5_jobs(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "step": 5,
        "step_name": "Market Opportunities",
        "status": "completed",
        "data": jobs,
    }


@router.post("/{session_id}/run-all")
def run_all(session_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Execute all pending steps 1 through 5 sequentially."""
    result = SessionService.run_all_steps(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "status": "completed",
        "message": "All 5 analysis steps completed successfully.",
        "data": result,
    }


@router.post("/batch-screen")
def batch_screen_candidates(payload: BatchScreeningRequest) -> Dict[str, Any]:
    """
    Sub-second real-time multi-candidate screening arena.
    Evaluates candidate batches at ~200ms per decision with deterministic selection matrices.
    """
    return SessionService.batch_screen_candidates(
        job_description=payload.job_description,
        candidates=payload.candidates,
    )
