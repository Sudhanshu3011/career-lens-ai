import json
import re
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models import AnalysisSession
from app.tools.pdf_extractor import extract_text
from app.tools.deterministic_parser import parse_resume_from_text
from app.tools.tech_keyword_extractor import extract_tech_keywords
from app.tools.candidate_scorer import score_resume_against_jd
from app.core.decision_engine import decision_engine
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
        extracted = extract_text(file_bytes)
        if not extracted or len(extracted.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short or empty. Please ensure the PDF contains readable text.",
            )

        session = AnalysisSession(
            resume_filename=filename,
            extracted_text=extracted,
            job_description=job_description.strip(),
            status="pending",
            current_step=1,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created zero-LLM analysis session id='{session.id}' for '{filename}'")
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> AnalysisSession:
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
        return session

    @staticmethod
    def list_sessions(db: Session, limit: int = 20) -> List[AnalysisSession]:
        return (
            db.query(AnalysisSession)
            .order_by(AnalysisSession.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def execute_step_1_parse(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 1: Document Structure & Section Parsing (Layout-Aware Zero-LLM)."""
        session = SessionService.get_session(db, session_id)
        logger.info(f"[Step 1] Parsing resume sections for session='{session_id}'")

        try:
            parsed_sections = parse_resume_from_text(session.extracted_text)
            if not parsed_sections:
                raise ValueError("Deterministic parser returned empty sections.")

            session.parsed_sections_json = json.dumps(parsed_sections)
            session.status = "parsed"
            session.current_step = 2
            session.error_message = None
            db.commit()
            db.refresh(session)
            return parsed_sections
        except Exception as exc:
            logger.exception(f"Step 1 failed for session='{session_id}'")
            session.error_message = str(exc)
            session.status = "failed"
            db.commit()
            code = _extract_status_code(exc)
            raise HTTPException(status_code=code, detail=f"Step 1 parsing failed [HTTP {code}]: {exc}")

    @staticmethod
    def execute_step_2_skills(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 2: Technical Skills Extraction against 450+ IT taxonomy."""
        session = SessionService.get_session(db, session_id)
        if not session.parsed_sections_json:
            raise HTTPException(status_code=400, detail="Step 1 (Parse) must be executed before Step 2.")

        logger.info(f"[Step 2] Extracting skills for session='{session_id}'")
        try:
            cand_tech = extract_tech_keywords(session.extracted_text)
            jd_tech = extract_tech_keywords(session.job_description)

            cand_skills = cand_tech.get("extracted_skills", [])
            jd_skills = jd_tech.get("extracted_skills", [])

            cand_lower = {s.lower(): s for s in cand_skills}
            jd_lower = {s.lower(): s for s in jd_skills}

            matched_skills = [jd_lower[k] for k in jd_lower if k in cand_lower]
            missing_skills = [jd_lower[k] for k in jd_lower if k not in cand_lower]

            skills_by_dom = cand_tech.get("skills_by_domain", {})
            tools = skills_by_dom.get("Cloud & DevOps", []) + skills_by_dom.get("Databases & Storage", [])

            skills_data = {
                "technical_skills": cand_skills,
                "tools_and_platforms": tools,
                "domains": list(skills_by_dom.keys()),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "skills_by_domain": skills_by_dom,
                "seniority": cand_tech.get("seniority", "Mid-Level"),
            }

            session.skills_data_json = json.dumps(skills_data)
            session.status = "skills_extracted"
            session.current_step = 3
            session.error_message = None
            db.commit()
            db.refresh(session)
            return skills_data
        except Exception as exc:
            logger.exception(f"Step 2 failed for session='{session_id}'")
            session.error_message = str(exc)
            session.status = "failed"
            db.commit()
            code = _extract_status_code(exc)
            raise HTTPException(status_code=code, detail=f"Step 2 skills extraction failed [HTTP {code}]: {exc}")

    @staticmethod
    def execute_step_3_decision(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 3: Deterministic Scoring & ConvAI Laya 4-Dimension Decision Model."""
        session = SessionService.get_session(db, session_id)
        if not session.skills_data_json or not session.parsed_sections_json:
            raise HTTPException(status_code=400, detail="Steps 1 and 2 must be executed before Step 3.")

        logger.info(f"[Step 3] Computing candidate decision for session='{session_id}'")
        try:
            skills_data = json.loads(session.skills_data_json)
            parsed_sections = json.loads(session.parsed_sections_json)

            decision_res = score_resume_against_jd(
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

            session.laya_decision_json = json.dumps(decision_res)
            session.status = "decision_computed"
            session.current_step = 4
            session.error_message = None
            db.commit()
            db.refresh(session)
            return decision_res
        except Exception as exc:
            logger.exception(f"Step 3 failed for session='{session_id}'")
            session.error_message = str(exc)
            session.status = "failed"
            db.commit()
            code = _extract_status_code(exc)
            raise HTTPException(status_code=code, detail=f"Step 3 decision failed [HTTP {code}]: {exc}")

    @staticmethod
    def execute_step_4_feedback(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 4: Diagnostics & Feedback."""
        session = SessionService.get_session(db, session_id)
        if not session.laya_decision_json or not session.skills_data_json:
            raise HTTPException(status_code=400, detail="Step 3 (Decision) must be executed before Step 4.")

        logger.info(f"[Step 4] Storing completed diagnostics state for session='{session_id}'")
        try:
            feedback_data = {
                "feedback": [],
                "strengths": [],
                "growth_areas": [],
                "actionable_steps": [],
                "elevation_roadmap": {},
                "role_summary": "",
                "diagnostic_reason": "",
                "rejection_flags": [],
            }

            session.feedback_json = json.dumps(feedback_data)
            session.status = "feedback_ready"
            session.current_step = 5
            session.error_message = None
            db.commit()
            db.refresh(session)
            return feedback_data
        except Exception as exc:
            logger.exception(f"Step 4 failed for session='{session_id}'")
            session.error_message = str(exc)
            session.status = "failed"
            db.commit()
            code = _extract_status_code(exc)
            raise HTTPException(status_code=code, detail=f"Step 4 feedback failed [HTTP {code}]: {exc}")

    @staticmethod
    def execute_step_5_jobs(db: Session, session_id: str) -> Dict[str, Any]:
        """Step 5: Candidate Scorecard & Seniority Opportunity Alignment."""
        session = SessionService.get_session(db, session_id)
        if not session.skills_data_json:
            raise HTTPException(status_code=400, detail="Step 2 (Skills) must be executed before Step 5.")

        logger.info(f"[Step 5] Finalizing candidate evaluation scorecard for session='{session_id}'")
        try:
            skills_data = json.loads(session.skills_data_json)
            decision_data = json.loads(session.laya_decision_json) if session.laya_decision_json else {}

            scorecard = {
                "seniority_tier": decision_data.get("seniority_tier", "mid_level"),
                "seniority_label": decision_data.get("seniority_label", "Mid-Level"),
                "final_score": decision_data.get("final_score", 7.0),
                "fit_score": decision_data.get("fit_score", 70.0),
                "high_hits_count": decision_data.get("high_hits_count", 0),
                "total_weighted_probability": decision_data.get("total_weighted_probability", 0.70),
                "overall_decision": decision_data.get("overall_decision", "Moderate match"),
                "breakdown": decision_data.get("breakdown", {}),
            }

            session.jobs_json = json.dumps([])
            session.status = "completed"
            session.error_message = None
            db.commit()
            db.refresh(session)
            return {"jobs": [], "scorecard": scorecard}
        except Exception as exc:
            logger.exception(f"Step 5 failed for session='{session_id}'")
            session.error_message = str(exc)
            session.status = "failed"
            db.commit()
            code = _extract_status_code(exc)
            raise HTTPException(status_code=code, detail=f"Step 5 jobs fetch failed [HTTP {code}]: {exc}")

    @staticmethod
    def run_all_steps(db: Session, session_id: str) -> Dict[str, Any]:
        """Executes all pending steps 1 through 5 sequentially without LLM calls."""
        session = SessionService.get_session(db, session_id)
        logger.info(f"Running all remaining zero-LLM steps for session='{session_id}' (starting at step {session.current_step})")

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
    def batch_screen_candidates(job_description: str, candidates: List[Any]) -> Dict[str, Any]:
        """Evaluates batch candidate profiles against job requirements with sub-second decision latency."""
        results = []
        total_start = time.perf_counter()

        for cand in candidates:
            cand_start = time.perf_counter()
            cand_skills = cand.skills if hasattr(cand, "skills") else cand.get("skills", [])
            candidate_skills = {
                "technical_skills": cand_skills,
                "tools_and_platforms": [
                    s for s in cand_skills
                    if s.lower() in ["docker", "kubernetes", "aws", "gcp", "azure", "git", "linux", "postgresql", "redis", "mongodb"]
                ],
                "domains": (
                    ["Artificial Intelligence", "Machine Learning"]
                    if any(k in s.lower() for s in cand_skills for k in ["ai", "ml", "torch", "yolo", "vision", "learning"])
                    else ["Software Engineering", "Backend"]
                ),
            }
            exp_text = cand.experience_text if hasattr(cand, "experience_text") else cand.get("experience_text", "")
            cand_id = cand.id if hasattr(cand, "id") else cand.get("id", "")
            cand_name = cand.name if hasattr(cand, "name") else cand.get("name", "")
            cand_title = cand.title if hasattr(cand, "title") else cand.get("title", "")
            cand_summary = cand.summary if hasattr(cand, "summary") else cand.get("summary", "")
            cand_edu = cand.education if hasattr(cand, "education") else cand.get("education", "")

            decision = decision_engine.evaluate_resume_match(
                candidate_skills=candidate_skills,
                experience_text=exp_text,
                job_description=job_description,
                education_text=cand_edu,
            )
            cand_latency_ms = round((time.perf_counter() - cand_start) * 1000, 1)
            logger.info(
                f"Candidate arena screened: '{cand_name}' ({cand_id}) in {cand_latency_ms}ms "
                f"-> Score={decision.get('fit_score', 0)}%, Decision='{decision.get('overall_decision', '')}'"
            )

            results.append({
                "candidate_id": cand_id,
                "name": cand_name,
                "title": cand_title,
                "skills": cand_skills,
                "summary": cand_summary,
                "latency_ms": cand_latency_ms,
                "decision": decision,
            })

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
