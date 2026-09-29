"""
CareerLens AI - Session Service
Manages session lifecycle and step-by-step sequential execution
persisting intermediate outputs with deterministic, sub-second latency.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.db.session import AnalysisSession
from app.repositories.session_repository import SessionRepository
from app.engines.parser.pdf_parser import extract_text
from app.engines.parser.deterministic_parser import parse_resume_from_text
from app.engines.extraction.tech_keywords import extract_tech_keywords
from app.engines.evaluation.candidate_scorer import score_resume_against_jd
from app.core.logger import get_logger

logger = get_logger(__name__)


def _extract_status_code(exc: Exception) -> int:
    """Extract real HTTP status code from exception if present, otherwise default to 500."""
    if isinstance(exc, HTTPException):
        return exc.status_code
    if hasattr(exc, "status_code") and isinstance(exc.status_code, int):
        return exc.status_code
    if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        return exc.response.status_code
    m = re.search(r"HTTP\s+(\d{3})", str(exc))
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return 500


def _normalize_candidate_item(cand: Any) -> Dict[str, Any]:
    """Normalizes candidate object or dict into structured attributes for batch arena screening."""
    cand_skills = cand.skills if hasattr(cand, "skills") else cand.get("skills", [])
    cloud_devops_keywords = {
        "docker",
        "kubernetes",
        "aws",
        "gcp",
        "azure",
        "git",
        "linux",
        "postgresql",
        "redis",
        "mongodb",
    }
    tools = [s for s in cand_skills if s.lower() in cloud_devops_keywords]

    ai_keywords = ["ai", "ml", "torch", "yolo", "vision", "learning"]
    is_aiml = any(k in s.lower() for s in cand_skills for k in ai_keywords)
    domains = (
        ["Artificial Intelligence", "Machine Learning"]
        if is_aiml
        else ["Software Engineering", "Backend"]
    )

    return {
        "id": cand.id if hasattr(cand, "id") else cand.get("id", ""),
        "name": cand.name if hasattr(cand, "name") else cand.get("name", ""),
        "title": cand.title if hasattr(cand, "title") else cand.get("title", ""),
        "summary": (
            cand.summary if hasattr(cand, "summary") else cand.get("summary", "")
        ),
        "education": (
            cand.education if hasattr(cand, "education") else cand.get("education", "")
        ),
        "experience": (
            cand.experience_text
            if hasattr(cand, "experience_text")
            else cand.get("experience_text", "")
        ),
        "skills": cand_skills,
        "tools": tools,
        "domains": domains,
    }


class SessionService:
    """
    Manages session lifecycle and step-by-step sequential execution
    persisting intermediate outputs into SQLite with ZERO LLM calls.
    100% deterministic, sub-second latency, zero token cost.
    """

    @staticmethod
    def create_session(
        db: Session,
        file_bytes: bytes,
        filename: str,
        job_description: str,
    ) -> AnalysisSession:
        """Creates analysis session by extracting text safely from uploaded PDF bytes."""
        try:
            extracted = extract_text(file_bytes)
        except Exception as exc:
            logger.warning(f"PDF text extraction failed for '{filename}': {exc}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract text from '{filename}'. Please ensure the PDF is not corrupted and contains extractable text.",
            )

        if not extracted or len(extracted.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short or empty. Please ensure the PDF contains readable text.",
            )

        session = SessionRepository.create(
            db=db,
            filename=filename,
            extracted_text=extracted,
            job_description=job_description.strip(),
        )
        logger.info(
            f"Created zero-LLM analysis session id='{session.id}' for '{filename}'"
        )
        return session

    @staticmethod
    def create_session_from_text(
        db: Session,
        extracted_text: str,
        filename: str,
        job_description: str,
    ) -> AnalysisSession:
        """Creates analysis session directly from pre-extracted text."""
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short or empty. Please ensure the PDF contains readable text.",
            )

        return SessionRepository.create(
            db=db,
            filename=filename,
            extracted_text=extracted_text,
            job_description=job_description.strip(),
        )

    @staticmethod
    def get_session(db: Session, session_id: str) -> AnalysisSession:
        session = SessionRepository.get_by_id(db, session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail=f"Session '{session_id}' not found."
            )
        return session

    @staticmethod
    def list_sessions(db: Session, limit: int = 20) -> List[AnalysisSession]:
        return SessionRepository.list_recent(db=db, limit=limit)

    @staticmethod
    def _execute_step_transaction(
        db: Session,
        session_id: str,
        step_number: int,
        step_name: str,
        next_step: int,
        success_status: str,
        json_attr_name: Optional[str],
        compute_fn: Callable[[AnalysisSession], Any],
        prerequisite_check: Optional[Callable[[AnalysisSession], Optional[str]]] = None,
    ) -> Any:
        """
        Standardized transaction wrapper for executing session steps.
        Enforces prerequisites, commits result, updates state, and centralizes error handling.
        """
        session = SessionService.get_session(db, session_id)
        if prerequisite_check:
            error_msg = prerequisite_check(session)
            if error_msg:
                raise HTTPException(status_code=400, detail=error_msg)

        logger.info(
            f"[Step {step_number}] Executing {step_name} for session='{session_id}'"
        )
        try:
            result = compute_fn(session)
            if json_attr_name:
                setattr(session, json_attr_name, json.dumps(result))
            session.status = success_status
            session.current_step = next_step
            session.error_message = None
            SessionRepository.save(db, session)
            return result
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception(f"Step {step_number} failed for session='{session_id}'")
            try:
                db.rollback()
                session.error_message = str(exc)
                session.status = "failed"
                SessionRepository.save(db, session)
            except Exception as save_err:
                logger.warning(
                    f"Could not persist failure status for session='{session_id}': {save_err}"
                )
            code = _extract_status_code(exc)
            raise HTTPException(
                status_code=code,
                detail=f"Step {step_number} {step_name.lower()} failed [HTTP {code}]: {exc}",
            )

    @staticmethod
    def execute_step_1_parse(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 1: Document Structure & Section Parsing (Layout-Aware Zero-LLM)."""

        def _parse(session: AnalysisSession) -> Dict[str, Any]:
            parsed = parse_resume_from_text(session.extracted_text)
            if not parsed:
                raise ValueError("Deterministic parser returned empty sections.")
            return parsed

        return SessionService._execute_step_transaction(
            db=db,
            session_id=session_id,
            step_number=1,
            step_name="Parsing",
            next_step=2,
            success_status="parsed",
            json_attr_name="parsed_sections_json",
            compute_fn=_parse,
        )

    @staticmethod
    def execute_step_2_skills(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 2: Technical Skills Extraction against 450+ IT taxonomy."""

        def _extract(session: AnalysisSession) -> Dict[str, Any]:
            cand_tech = extract_tech_keywords(session.extracted_text)
            jd_tech = extract_tech_keywords(session.job_description)

            cand_skills = cand_tech.get("extracted_skills", [])
            jd_skills = jd_tech.get("extracted_skills", [])
            cand_lower = {s.lower(): s for s in cand_skills}
            jd_lower = {s.lower(): s for s in jd_skills}

            matched_skills = [jd_lower[k] for k in jd_lower if k in cand_lower]
            missing_skills = [jd_lower[k] for k in jd_lower if k not in cand_lower]
            skills_by_dom = cand_tech.get("skills_by_domain", {})
            tools = skills_by_dom.get("Cloud & DevOps", []) + skills_by_dom.get(
                "Databases & Storage", []
            )

            return {
                "technical_skills": cand_skills,
                "tools_and_platforms": tools,
                "domains": list(skills_by_dom.keys()),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "skills_by_domain": skills_by_dom,
                "seniority": cand_tech.get("seniority", "Mid-Level"),
            }

        return SessionService._execute_step_transaction(
            db=db,
            session_id=session_id,
            step_number=2,
            step_name="Skills Extraction",
            next_step=3,
            success_status="skills_extracted",
            json_attr_name="skills_data_json",
            compute_fn=_extract,
            prerequisite_check=lambda s: (
                "Step 1 (Parse) must be executed before Step 2."
                if not s.parsed_sections_json
                else None
            ),
        )

    @staticmethod
    def execute_step_3_decision(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 3: Deterministic Scoring & ConvAI Laya 4-Dimension Decision Model."""

        def _score(session: AnalysisSession) -> Dict[str, Any]:
            skills_data = json.loads(session.skills_data_json or "{}")
            parsed_sections = json.loads(session.parsed_sections_json or "{}")
            return score_resume_against_jd(
                resume_data={
                    "tech_skills": skills_data.get("technical_skills", []),
                    "tools_and_platforms": skills_data.get("tools_and_platforms", []),
                    "domains": skills_data.get("domains", []),
                    "skills_by_domain": skills_data.get("skills_by_domain", {}),
                    "experience": parsed_sections.get("experience", ""),
                    "summary": parsed_sections.get("summary", ""),
                    "raw_text": session.extracted_text,
                },
                job_description=session.job_description,
            )

        return SessionService._execute_step_transaction(
            db=db,
            session_id=session_id,
            step_number=3,
            step_name="Decision",
            next_step=4,
            success_status="decision_computed",
            json_attr_name="laya_decision_json",
            compute_fn=_score,
            prerequisite_check=lambda s: (
                "Steps 1 and 2 must be executed before Step 3."
                if (not s.skills_data_json or not s.parsed_sections_json)
                else None
            ),
        )

    @staticmethod
    def execute_step_4_feedback(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 4: Diagnostics & Feedback."""

        def _feedback(session: AnalysisSession) -> Dict[str, Any]:
            return {
                "feedback": [],
                "strengths": [],
                "growth_areas": [],
                "actionable_steps": [],
                "elevation_roadmap": {},
                "role_summary": "",
                "diagnostic_reason": "",
                "rejection_flags": [],
            }

        return SessionService._execute_step_transaction(
            db=db,
            session_id=session_id,
            step_number=4,
            step_name="Feedback",
            next_step=5,
            success_status="feedback_ready",
            json_attr_name="feedback_json",
            compute_fn=_feedback,
            prerequisite_check=lambda s: (
                "Step 3 (Decision) must be executed before Step 4."
                if (not s.laya_decision_json or not s.skills_data_json)
                else None
            ),
        )

    @staticmethod
    def execute_step_5_jobs(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 5: Candidate Scorecard & Seniority Opportunity Alignment."""

        def _scorecard(session: AnalysisSession) -> Dict[str, Any]:
            decision_data = json.loads(session.laya_decision_json or "{}")
            scorecard = {
                "seniority_tier": decision_data.get("seniority_tier", "mid_level"),
                "seniority_label": decision_data.get("seniority_label", "Mid-Level"),
                "final_score": decision_data.get("final_score", 7.0),
                "fit_score": decision_data.get("fit_score", 70.0),
                "high_hits_count": decision_data.get("high_hits_count", 0),
                "total_weighted_probability": decision_data.get(
                    "total_weighted_probability", 0.70
                ),
                "overall_decision": decision_data.get(
                    "overall_decision", "Moderate match"
                ),
                "breakdown": decision_data.get("breakdown", {}),
            }
            # Maintain backward compatibility with jobs_data as an array
            session.jobs_json = json.dumps([])
            return {"jobs": [], "scorecard": scorecard}

        return SessionService._execute_step_transaction(
            db=db,
            session_id=session_id,
            step_number=5,
            step_name="Jobs Fetch",
            next_step=5,
            success_status="completed",
            json_attr_name=None,
            compute_fn=_scorecard,
            prerequisite_check=lambda s: (
                "Step 2 (Skills) must be executed before Step 5."
                if not s.skills_data_json
                else None
            ),
        )

    @staticmethod
    def run_all_steps(db: Session, session_id: str) -> Dict[str, Any]:
        """Executes all pending steps 1 through 5 sequentially without LLM calls."""
        session = SessionService.get_session(db, session_id)
        logger.info(
            f"Running all remaining zero-LLM steps for session='{session_id}' (starting at step {session.current_step})"
        )

        if not session.parsed_sections_json:
            SessionService.execute_step_1_parse(db, session_id)
        if not session.skills_data_json:
            SessionService.execute_step_2_skills(db, session_id)
        if not session.laya_decision_json:
            SessionService.execute_step_3_decision(db, session_id)
        if not session.feedback_json:
            SessionService.execute_step_4_feedback(db, session_id)
        if not session.jobs_json:
            SessionService.execute_step_5_jobs(db, session_id)

        session = SessionService.get_session(db, session_id)
        return {
            "session_id": session.id,
            "status": session.status,
            "current_step": session.current_step,
            "parsed_sections": json.loads(session.parsed_sections_json or "{}"),
            "skills_data": json.loads(session.skills_data_json or "{}"),
            "laya_decision": json.loads(session.laya_decision_json or "{}"),
            "feedback_data": json.loads(session.feedback_json or "{}"),
            "jobs_data": json.loads(session.jobs_json or "[]"),
        }

    @staticmethod
    def batch_screen_candidates(
        job_description: str, candidates: List[Any]
    ) -> Dict[str, Any]:
        """Evaluates batch candidate profiles against job requirements with sub-second decision latency."""
        results = []
        total_start = time.perf_counter()

        for raw_cand in candidates:
            cand_start = time.perf_counter()
            cand = _normalize_candidate_item(raw_cand)

            decision = score_resume_against_jd(
                resume_data={
                    "tech_skills": cand["skills"],
                    "tools_and_platforms": cand["tools"],
                    "domains": cand["domains"],
                    "experience": cand["experience"],
                    "summary": cand["summary"],
                    "education": cand["education"],
                },
                job_description=job_description,
            )
            cand_latency_ms = round((time.perf_counter() - cand_start) * 1000, 1)
            logger.info(
                f"Candidate arena screened: '{cand['name']}' ({cand['id']}) in {cand_latency_ms}ms "
                f"-> Score={decision.get('fit_score', 0)}%, Decision='{decision.get('overall_decision', '')}'"
            )

            results.append(
                {
                    "candidate_id": cand["id"],
                    "name": cand["name"],
                    "title": cand["title"],
                    "skills": cand["skills"],
                    "summary": cand["summary"],
                    "latency_ms": cand_latency_ms,
                    "decision": decision,
                }
            )

        results.sort(key=lambda x: x["decision"].get("final_score", 0), reverse=True)
        total_latency_ms = round((time.perf_counter() - total_start) * 1000, 1)
        logger.info(
            f"Batch candidates arena complete: screened={len(results)} in {total_latency_ms}ms "
            f"(avg {round(total_latency_ms / max(1, len(results)), 1)}ms/candidate)"
        )

        return {
            "total_screened": len(results),
            "total_latency_ms": total_latency_ms,
            "average_latency_ms": round(total_latency_ms / max(1, len(results)), 1),
            "results": results,
        }
