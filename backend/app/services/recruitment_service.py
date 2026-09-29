"""
CareerLens AI - Recruitment Intelligence Service Layer
Orchestrates:
1. Dynamic JD Question Synthesis with SHA-256 DB Caching
2. Recruiter Question Review & Precondition Validation (Mandatory Human Gate)
3. Rate-Limited Resume Parsing (1 req/min) with PDF Byte Hash Caching
4. Granular Parsed Resume Data Access
5. Memory-Throttled Evaluation (Max 2 Concurrent Laya Inferences) with Real-Time Streaming
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logger import get_logger
from app.engines.evaluation.speculative_fanout import speculative_evaluator
from app.engines.jev.client import JevClient
from app.engines.laya.client import LayaClient
from app.engines.parser.groq_parser import UniversalResumeParser
from app.engines.parser.pdf_extractor import extract_text_and_links_from_pdf
from app.engines.question_factory.adapter import BlueprintToEngineAdapter
from app.engines.question_factory.generator import DynamicQuestionFactory
from app.models.db.candidate_evaluation import CandidateEvaluation
from app.models.db.job_requisition import JobRequisition
from app.models.db.parsed_resume import ParsedResume
from app.models.domain.dynamic_blueprint import EvaluationQuestionsBlueprint
from app.models.domain.resume_sections import ResumeParsedSections
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.recruitment import (
    CandidateEvaluationItem,
    EvaluationQuestionItem,
    JobAnalyzeResponse,
    JobEvaluationSummaryResponse,
    JobQuestionsUpdateResponse,
    ResumeDetailResponse,
    ResumeUploadBatchResponse,
    ResumeUploadResponseItem,
)

logger = get_logger(__name__)

# Strictly limits concurrent Laya / Jev tensor evaluations to 2 parallel tasks
laya_evaluation_semaphore = asyncio.Semaphore(2)


class RecruitmentService:
    """Service handling the end-to-end recruitment intelligence workflow."""

    def __init__(self) -> None:
        self.blueprint_generator = DynamicQuestionFactory()
        self.resume_parser = UniversalResumeParser()

    # =========================================================================
    # Phase 1: Dynamic Question Synthesis & JD Caching
    # =========================================================================

    async def analyze_job_requisition(
        self,
        db: Session,
        role_title: str,
        job_description: str,
    ) -> JobAnalyzeResponse:
        """
        Analyzes a job description, using SHA-256 cache lookup to avoid redundant LLM calls.
        Returns the job_id, dynamic blueprint, and initial compiled questions.
        """
        jd_hash = JobRepository.compute_hash(role_title, job_description)
        existing_job = JobRepository.get_by_hash(db, jd_hash)

        if existing_job and existing_job.blueprint_json:
            logger.info("RecruitmentService: Cache hit for JD hash %s", jd_hash)
            blueprint_dict = json.loads(existing_job.blueprint_json)
            questions_dict: Dict[str, EvaluationQuestionItem] = {}

            if existing_job.configured_questions_json:
                raw_q = json.loads(existing_job.configured_questions_json)
                questions_dict = {k: EvaluationQuestionItem(**v) for k, v in raw_q.items()}
            else:
                blueprint = EvaluationQuestionsBlueprint(**blueprint_dict)
                questions_dict = BlueprintToEngineAdapter.blueprint_to_question_items(blueprint)

            return JobAnalyzeResponse(
                job_id=existing_job.id,
                role_title=existing_job.role_title,
                jd_hash=existing_job.jd_hash,
                is_reviewed=existing_job.is_reviewed,
                blueprint=blueprint_dict,
                questions=questions_dict,
                cached=True,
                message="Retrieved existing cached evaluation blueprint and questions from database.",
            )

        logger.info("RecruitmentService: Cache miss for JD hash %s. Synthesizing blueprint via LLM...", jd_hash)
        blueprint = await self.blueprint_generator.generate_blueprint(
            job_description=job_description,
            role_title=role_title,
        )
        blueprint_dict = blueprint.model_dump()
        question_items = BlueprintToEngineAdapter.blueprint_to_question_items(blueprint)
        questions_dict_serializable = {k: v.model_dump() for k, v in question_items.items()}

        new_job = JobRepository.create(
            db=db,
            role_title=role_title,
            job_description=job_description,
            blueprint_json=json.dumps(blueprint_dict),
            configured_questions_json=json.dumps(questions_dict_serializable),
            is_reviewed=False,
        )

        return JobAnalyzeResponse(
            job_id=new_job.id,
            role_title=new_job.role_title,
            jd_hash=new_job.jd_hash,
            is_reviewed=False,
            blueprint=blueprint_dict,
            questions=question_items,
            cached=False,
            message="Dynamic evaluation blueprint and questions synthesized successfully.",
        )

    def get_job(self, db: Session, job_id: str) -> JobRequisition:
        """Retrieves a JobRequisition by ID or raises 404."""
        job = JobRepository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job requisition with id '{job_id}' not found.",
            )
        return job

    # =========================================================================
    # Phase 2: Human-in-the-Loop Question Review & Precondition Validation
    # =========================================================================

    def update_job_questions(
        self,
        db: Session,
        job_id: str,
        questions: Dict[str, EvaluationQuestionItem],
    ) -> JobQuestionsUpdateResponse:
        """
        Updates recruiter-configured questions, saves dealbreaker toggles,
        and marks is_reviewed = True. This is a mandatory gate before evaluation.
        """
        job = self.get_job(db, job_id)
        serialized_questions = {k: v.model_dump() for k, v in questions.items()}
        mandatory_count = sum(1 for v in questions.values() if v.is_mandatory)

        JobRepository.update_questions(
            db=db,
            job=job,
            configured_questions_json=json.dumps(serialized_questions),
            is_reviewed=True,
        )

        logger.info(
            "RecruitmentService: Job %s questions reviewed and saved. Total: %d, Mandatory gates: %d",
            job_id,
            len(questions),
            mandatory_count,
        )

        return JobQuestionsUpdateResponse(
            job_id=job.id,
            is_reviewed=True,
            total_questions=len(questions),
            mandatory_gates_count=mandatory_count,
            questions=questions,
            message="Questions successfully reviewed and locked for candidate evaluation.",
        )

    # =========================================================================
    # Phase 3: Resume Ingestion & Rate-Limited Sequential Parsing
    # =========================================================================

    async def upload_resumes(
        self,
        db: Session,
        files: List[UploadFile],
    ) -> ResumeUploadBatchResponse:
        """
        Ingests 1 to 15 resumes. For each file:
        - Computes SHA-256 byte hash.
        - If already parsed in DB -> returns instantly as cached (0s delay).
        - If new -> registers in DB and enqueues for 1 req/min rate-limited parsing.
        """
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one resume file must be uploaded.",
            )

        items: List[ResumeUploadResponseItem] = []
        cached_count = 0
        queued_count = 0
        newly_queued_records: List[tuple[str, str, bytes]] = []

        for idx, file in enumerate(files):
            filename = file.filename or f"resume_{idx + 1}.pdf"
            pdf_bytes = await file.read()
            file_hash = ResumeRepository.compute_file_hash(pdf_bytes)

            existing_resume = ResumeRepository.get_by_hash(db, file_hash)
            if existing_resume and existing_resume.status == "completed":
                cached_count += 1
                items.append(
                    ResumeUploadResponseItem(
                        resume_id=existing_resume.id,
                        filename=existing_resume.filename,
                        file_hash=existing_resume.file_hash,
                        file_size_bytes=existing_resume.file_size_bytes,
                        status="cached",
                        eta_seconds=0,
                        message="Instant cache hit: Parsed data retrieved from database.",
                    )
                )
            else:
                queued_count += 1
                if existing_resume:
                    resume_record = existing_resume
                    resume_record.status = "queued"
                    resume_record.error_message = None
                    db.commit()
                else:
                    resume_record = ResumeRepository.create(
                        db=db,
                        file_hash=file_hash,
                        filename=filename,
                        file_size_bytes=len(pdf_bytes),
                        status="queued",
                    )
                newly_queued_records.append((resume_record.id, filename, pdf_bytes))
                eta = (queued_count - 1) * 60  # Rate limit: 60s per item
                items.append(
                    ResumeUploadResponseItem(
                        resume_id=resume_record.id,
                        filename=filename,
                        file_hash=file_hash,
                        file_size_bytes=len(pdf_bytes),
                        status="queued",
                        eta_seconds=eta,
                        message=f"Queued for sequential 1 req/min LLM parsing. Estimated wait: {eta}s.",
                    )
                )

        # Trigger background parsing for newly queued resumes
        if newly_queued_records:
            asyncio.create_task(self._process_resume_queue(newly_queued_records))

        return ResumeUploadBatchResponse(
            total_uploaded=len(files),
            cached_count=cached_count,
            queued_count=queued_count,
            resumes=items,
        )

    async def _process_resume_queue(
        self,
        records: List[tuple[str, str, bytes]],
    ) -> None:
        """
        Background worker that sequentially parses resumes using the rate limiter.
        Updates each resume record in DB upon completion so clients can fetch or stream it immediately.
        """
        for resume_id, filename, pdf_bytes in records:
            # Use a fresh DB session for the background task
            db = SessionLocal()
            try:
                # Mark parsing
                current = ResumeRepository.get_by_id(db, resume_id)
                if not current:
                    continue
                current.status = "parsing"
                db.commit()

                # Parse PDF text and extract links
                raw_text, links = extract_text_and_links_from_pdf(pdf_bytes)

                # Execute rate-limited structured parsing
                parsed_sections = await self.resume_parser.parse_resume_text(
                    resume_text=raw_text,
                    filename=current.filename,
                    initial_links=links,
                )

                ResumeRepository.update_completed(
                    db=db,
                    resume=current,
                    parsed_sections_json=json.dumps(parsed_sections.model_dump()),
                    raw_text=raw_text,
                    portfolio_links_json=json.dumps(links),
                )
                logger.info(
                    "Background worker completed parsing resume %s (%s)",
                    current.id,
                    current.filename,
                )
            except Exception as exc:
                logger.error(
                    "Background worker failed to parse resume %s (%s): %s",
                    resume_id,
                    filename,
                    exc,
                    exc_info=True,
                )
                try:
                    current = ResumeRepository.get_by_id(db, resume_id)
                    if current:
                        ResumeRepository.update_failed(db, current, str(exc))
                except Exception as inner_exc:
                    logger.error(
                        "Failed to update failed status for resume %s: %s",
                        resume_id,
                        inner_exc,
                    )
            finally:
                db.close()

    # =========================================================================
    # Phase 4: Granular Parsed Resume Details
    # =========================================================================

    def get_resume_detail(self, db: Session, resume_id: str) -> ResumeDetailResponse:
        """Retrieves granular 6-section parsed resume data for a specific candidate."""
        resume = ResumeRepository.get_by_id(db, resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parsed resume with id '{resume_id}' not found.",
            )

        parsed_dict = None
        if resume.parsed_sections_json:
            try:
                parsed_dict = json.loads(resume.parsed_sections_json)
            except Exception:
                parsed_dict = None

        links = []
        if resume.portfolio_links_json:
            try:
                links = json.loads(resume.portfolio_links_json)
            except Exception:
                links = []

        return ResumeDetailResponse(
            resume_id=resume.id,
            filename=resume.filename,
            file_hash=resume.file_hash,
            file_size_bytes=resume.file_size_bytes,
            status=resume.status,
            parsed_sections=parsed_dict,
            raw_text=resume.raw_text,
            portfolio_links=links,
            error_message=resume.error_message,
        )

    async def reparse_resume(self, db: Session, resume_id: str) -> ResumeUploadResponseItem:
        """Retries structured parsing for a candidate resume that was disrupted or produced incomplete data."""
        resume = ResumeRepository.get_by_id(db, resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with id '{resume_id}' not found.",
            )

        if not resume.raw_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Raw resume text not found. Please re-upload the PDF document.",
            )

        resume.status = "parsing"
        resume.error_message = None
        resume.parsed_sections_json = None
        db.commit()

        # Trigger background re-parse
        asyncio.create_task(self._reparse_single_resume(resume.id))

        return ResumeUploadResponseItem(
            resume_id=resume.id,
            filename=resume.filename,
            file_hash=resume.file_hash,
            file_size_bytes=resume.file_size_bytes,
            status="parsing",
            eta_seconds=20,
            message="Re-parsing initiated with high-precision model.",
        )

    async def _reparse_single_resume(self, resume_id: str) -> None:
        db = SessionLocal()
        try:
            resume = ResumeRepository.get_by_id(db, resume_id)
            if not resume:
                return
            links = json.loads(resume.portfolio_links_json) if resume.portfolio_links_json else []
            parsed_sections = await self.resume_parser.parse_resume_text(
                resume_text=resume.raw_text,
                filename=resume.filename,
                initial_links=links,
            )
            ResumeRepository.update_completed(
                db=db,
                resume=resume,
                parsed_sections_json=json.dumps(parsed_sections.model_dump()),
                raw_text=resume.raw_text,
                portfolio_links_json=json.dumps(links),
            )
            logger.info("Successfully re-parsed resume %s (%s)", resume.id, resume.filename)
        except Exception as exc:
            logger.error("Re-parse failed for %s: %s", resume_id, exc, exc_info=True)
            current = ResumeRepository.get_by_id(db, resume_id)
            if current:
                ResumeRepository.update_failed(
                    db=db,
                    resume=current,
                    error_message=str(exc) if "Please" in str(exc) else f"Parsing disrupted ({exc}). Data was not saved. Please try parsing again.",
                )
        finally:
            db.close()


    # =========================================================================
    # Phase 5: Throttled Candidate Evaluation & Streaming
    # =========================================================================

    def _prepare_job_evaluation(
        self,
        db: Session,
        job_id: str,
        resume_ids: List[str],
    ) -> tuple[JobRequisition, Dict[str, Any], Dict[str, Dict[str, Any]], List[ParsedResume]]:
        """Validates precondition gate (is_reviewed == True) and prepares questions & resumes."""
        job = self.get_job(db, job_id)
        if not job.is_reviewed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Job requisition '{job_id}' questions have not been reviewed and confirmed yet. "
                    f"Recruiter review is a mandatory precondition: Call PUT /api/v1/jobs/{job_id}/questions first."
                ),
            )

        if not job.blueprint_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation blueprint missing for job requisition.",
            )

        blueprint = EvaluationQuestionsBlueprint(**json.loads(job.blueprint_json))

        # Compile configured questions
        if job.configured_questions_json:
            configured_dict = json.loads(job.configured_questions_json)
            questions, gate_registry = BlueprintToEngineAdapter.compile_from_configured_questions(
                configured_dict, blueprint
            )
        else:
            questions, gate_registry = BlueprintToEngineAdapter.compile_questions(blueprint)

        resumes = ResumeRepository.get_by_ids(db, resume_ids)
        if not resumes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="None of the specified resume IDs were found in the database.",
            )

        return job, questions, gate_registry, resumes

    async def evaluate_single_candidate(
        self,
        db: Session,
        job: JobRequisition,
        resume: ParsedResume,
        questions: Dict[str, Any],
        gate_registry: Dict[str, Dict[str, Any]],
        pipeline: str = "laya",
    ) -> CandidateEvaluationItem:
        """
        Evaluates a single candidate under laya_evaluation_semaphore (max 2 parallel).
        Persists CandidateEvaluation in database and returns the result item.
        """
        if resume.status != "completed" or not resume.parsed_sections_json:
            is_failed = resume.status == "failed"
            return CandidateEvaluationItem(
                evaluation_id=f"eval_pending_{resume.id}",
                job_id=job.id,
                resume_id=resume.id,
                candidate_name=resume.filename,
                pipeline=pipeline,
                fit_score=0.0,
                verdict="REJECT" if is_failed else "HOLD",
                status="failed" if is_failed else "pending_parsing",
                breakdown={},
                portfolio_links=[],
                projects=[],
                error_message=resume.error_message or (
                    f"Resume extraction failed: unreadable or corrupted document."
                    if is_failed
                    else f"Resume '{resume.filename}' has not completed parsing yet (status: {resume.status})."
                ),
            )

        sections = ResumeParsedSections(**json.loads(resume.parsed_sections_json))
        candidate_state = sections.to_typesafe_state()

        async with laya_evaluation_semaphore:
            logger.info("Evaluating candidate '%s' under semaphore (pipeline=%s)", sections.candidate_name, pipeline)
            if pipeline.lower() == "jev":
                jev_client = JevClient.get_instance()
                answers = await jev_client.evaluate_fanout(candidate_state, questions)
                engine_name = "jev"
            else:
                laya_client = LayaClient.get_instance()
                answers = await laya_client.evaluate_fanout(candidate_state, questions)
                engine_name = "laya"

            verdict = speculative_evaluator.evaluate(
                candidate_sections=sections,
                answers=answers,
                gate_registry=gate_registry,
                engine_name=engine_name,
            )

        # Save to DB
        existing_eval = EvaluationRepository.get_by_job_and_resume(db, job.id, resume.id)
        if existing_eval:
            eval_record = EvaluationRepository.update_completed(
                db=db,
                evaluation=existing_eval,
                fit_score=verdict.fit_score,
                verdict=verdict.overall_decision,
                verdict_json=json.dumps(verdict.model_dump()),
            )
        else:
            eval_record = EvaluationRepository.create(
                db=db,
                job_id=job.id,
                resume_id=resume.id,
                candidate_name=verdict.candidate_name,
                pipeline=pipeline,
                status="completed",
                fit_score=verdict.fit_score,
                verdict=verdict.overall_decision,
                verdict_json=json.dumps(verdict.model_dump()),
            )

        return CandidateEvaluationItem(
            evaluation_id=eval_record.id,
            job_id=job.id,
            resume_id=resume.id,
            candidate_name=verdict.candidate_name,
            pipeline=pipeline,
            fit_score=verdict.fit_score,
            verdict=verdict.overall_decision,
            status="completed",
            breakdown=verdict.breakdown.model_dump(),
            portfolio_links=sections.portfolio_links,
            projects=[p.model_dump() for p in sections.projects],
        )

    async def evaluate_candidates_sync(
        self,
        db: Session,
        job_id: str,
        resume_ids: List[str],
        pipeline: str = "laya",
    ) -> JobEvaluationSummaryResponse:
        """Evaluates a batch of candidates synchronously (throttled at max 2 parallel Laya instances)."""
        job, questions, gate_registry, resumes = self._prepare_job_evaluation(
            db=db,
            job_id=job_id,
            resume_ids=resume_ids,
        )

        results: List[CandidateEvaluationItem] = []
        for resume in resumes:
            item = await self.evaluate_single_candidate(
                db=db,
                job=job,
                resume=resume,
                questions=questions,
                gate_registry=gate_registry,
                pipeline=pipeline,
            )
            results.append(item)

        results.sort(key=lambda x: x.fit_score, reverse=True)
        top_candidates = results[:3]

        return JobEvaluationSummaryResponse(
            job_id=job.id,
            total_evaluated=len(results),
            top_candidates=top_candidates,
            evaluations=results,
        )

    async def stream_candidate_evaluations(
        self,
        db: Session,
        job_id: str,
        resume_ids: List[str],
        pipeline: str = "laya",
    ) -> AsyncGenerator[str, None]:
        """
        Streams candidate evaluations in real-time as Server-Sent Events (SSE).
        Yields an event immediately as each individual candidate finishes inference!
        """
        job, questions, gate_registry, resumes = self._prepare_job_evaluation(
            db=db,
            job_id=job_id,
            resume_ids=resume_ids,
        )

        yield f"event: started\ndata: {json.dumps({'job_id': job.id, 'total_candidates': len(resumes)})}\n\n"

        completed_items: List[CandidateEvaluationItem] = []

        for resume in resumes:
            item = await self.evaluate_single_candidate(
                db=db,
                job=job,
                resume=resume,
                questions=questions,
                gate_registry=gate_registry,
                pipeline=pipeline,
            )
            completed_items.append(item)
            payload = {
                "event": "candidate_evaluated",
                "evaluation": item.model_dump(),
            }
            yield f"event: candidate_evaluated\ndata: {json.dumps(payload)}\n\n"

        completed_items.sort(key=lambda x: x.fit_score, reverse=True)
        summary = {
            "event": "evaluation_completed",
            "job_id": job.id,
            "total_evaluated": len(completed_items),
            "top_candidates": [c.model_dump() for c in completed_items[:3]],
        }
        yield f"event: completed\ndata: {json.dumps(summary)}\n\n"


# Global singleton instance
recruitment_service = RecruitmentService()
