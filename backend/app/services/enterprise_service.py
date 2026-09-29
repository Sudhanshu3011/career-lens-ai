"""
CareerLens AI - Enterprise Bulk Resume Screening Service

Business logic for batch candidate evaluation, multi-dimensional scoring,
concurrent async processing, and Top 3 candidate ranking.
"""

from __future__ import annotations

import asyncio
import gc
import time
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, UploadFile, status

from app.services.typesafe_pipeline import evaluate_candidate_typesafe
from app.engines.extraction.jd_extractor import extract_job_profile
from app.models.domain.job import JobProfile
from app.core.validators import validate_pdf_metadata
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def validate_screening_batch(resumes: List[UploadFile]) -> None:
    """
    Validates batch constraints and verifies that every uploaded file is a valid PDF
    by both filename extension and MIME type.
    """
    if not resumes:
        logger.warning("Batch validation failed: No resume files provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume files provided. Please upload at least 1 PDF resume.",
        )

    if len(resumes) > settings.MAX_BATCH_SIZE:
        logger.warning(
            f"Batch validation failed: {len(resumes)} resumes uploaded (max {settings.MAX_BATCH_SIZE} allowed)"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_BATCH_SIZE} resumes allowed per batch. You uploaded {len(resumes)}.",
        )

    for file in resumes:
        validate_pdf_metadata(file)

    logger.info(
        f"Validated screening batch containing {len(resumes)} valid PDF file(s)"
    )


def _build_fallback_record(
    idx: int, filename: str, error_message: str
) -> Dict[str, Any]:
    """Generates a safe fallback record for a corrupted or unparsable resume."""
    clean_filename = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
    return {
        "candidate_id": f"cand-{idx + 1}",
        "name": clean_filename.title(),
        "filename": filename,
        "fit_score": 0.0,
        "raw_score": 0.0,
        "decision": "REJECT",
        "seniority_tier": "mid_level",
        "seniority_label": "Mid-Level",
        "target_seniority_tier": "mid_level",
        "target_seniority_label": "Mid-Level",
        "candidate_seniority_tier": "mid_level",
        "candidate_seniority_label": "Mid-Level",
        "seniority_alignment": "ALIGNED",
        "high_hits_count": 0,
        "raw_weighted_probability": 0.0,
        "penalty_applied": 0.0,
        "total_weighted_probability": 0.0,
        "breakdown": {
            "technical_requirements": 0,
            "experience_requirements": 0,
            "domain_alignment": 0,
            "education_alignment": 0,
            "evidence_strength": 0,
        },
        "parameter_evaluations": {},
        "skills": [],
        "tools": [],
        "domains": [],
        "decision_reason": f"Processing notice: {error_message}",
        "technical_overlap": {
            "matched_skills": [],
            "missing_jd_skills": [],
            "candidate_bonus_skills": [],
            "skill_overlap_percentage": 0.0,
        },
    }


async def _evaluate_single_candidate(
    file: UploadFile,
    job_profile: JobProfile,
    idx: int,
    pipeline_mode: str = "typesafe",
    semaphore: Optional[asyncio.Semaphore] = None,
) -> Dict[str, Any] | None:
    """
    Asynchronously reads and evaluates a single resume file using the modular TypeSafe pipeline.
    Gates concurrent execution with a Semaphore to prevent CPU thread thrashing and PyTorch memory spikes.
    """
    filename = file.filename or f"resume_{idx+1}.pdf"

    async def _execute_evaluation():
        pdf_bytes = None
        try:
            pdf_bytes = await file.read()
            if not pdf_bytes or len(pdf_bytes) < 100:
                logger.warning(
                    f"Skipping empty or corrupt PDF resume: {filename} ({len(pdf_bytes) if pdf_bytes else 0} bytes)"
                )
                return None

            record = await asyncio.to_thread(
                evaluate_candidate_typesafe,
                pdf_bytes=pdf_bytes,
                filename=filename,
                job_profile=job_profile,
                idx=idx,
                pipeline_mode=pipeline_mode,
            )
            return record

        except Exception as exc:
            logger.error(
                f"Failed to process candidate {filename}: {exc}", exc_info=True
            )
            return _build_fallback_record(idx, filename, str(exc))
        finally:
            # Free in-memory PDF byte buffers immediately
            del pdf_bytes

    if semaphore:
        async with semaphore:
            return await _execute_evaluation()
    return await _execute_evaluation()


def _rank_and_flag_candidates(candidates: List[Dict[str, Any]]) -> None:
    """Sorts candidates descending by unified total weighted probability and assigns rank badges."""
    candidates.sort(
        key=lambda c: (
            c.get("total_weighted_probability", 0.0),
            c.get("fit_score", 0.0),
        ),
        reverse=True,
    )
    for rank_idx, cand in enumerate(candidates):
        cand["rank"] = rank_idx + 1
        cand["is_top_3"] = rank_idx < 3
        cand["is_top_5"] = rank_idx < 5


async def screen_resumes_batch(
    job_role: str,
    job_description: str,
    resumes: List[UploadFile],
    pipeline_mode: str = "typesafe",
    approved_requirements: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Executes concurrent batch screening of resumes against the target job description:
    1. Validates upload batch size and file MIME types.
    2. Constructs structured JobProfile (Stage 1 JD analysis or recruiter-approved criteria).
    3. Concurrently evaluates candidates using bounded concurrency semaphore (prevents OOM).
    4. Ranks candidates and flags top shortlisted profiles.
    """
    validate_screening_batch(resumes)

    start_time = time.perf_counter()
    logger.info(
        f"Starting TypeSafe batch screening pipeline: Role='{job_role}', Pipeline='{pipeline_mode}', "
        f"BatchSize={len(resumes)}, ApprovedReqs={len(approved_requirements) if approved_requirements else 0}, "
        f"JDLength={len(job_description)} chars, ConcurrencyLimit={settings.MAX_CONCURRENT_EVALUATIONS}"
    )

    # 1. Normalize JD into structured JobProfile via TypeSafe extractor
    job_profile: JobProfile = await asyncio.to_thread(
        extract_job_profile,
        job_description=job_description,
        job_role=job_role,
        pipeline_mode=pipeline_mode,
        approved_requirements=approved_requirements,
    )

    # 2. Process candidates with bounded concurrency semaphore to prevent memory exhaustion
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_EVALUATIONS)

    evaluation_tasks = [
        _evaluate_single_candidate(
            file=file,
            job_profile=job_profile,
            idx=idx,
            pipeline_mode=pipeline_mode,
            semaphore=semaphore,
        )
        for idx, file in enumerate(resumes)
    ]
    raw_results = await asyncio.gather(*evaluation_tasks)
    candidates = [res for res in raw_results if res is not None]

    # Explicit garbage collection after large batches (10-20 resumes) to reclaim tensor memory
    if len(resumes) >= 4:
        gc.collect()

    # 3. Rank and assign badges
    _rank_and_flag_candidates(candidates)

    elapsed = time.perf_counter() - start_time
    avg_score = (
        round(sum(c["fit_score"] for c in candidates) / len(candidates), 1)
        if candidates
        else 0.0
    )
    selected_count = sum(1 for c in candidates if c["decision"] == "SELECT")

    top_name = candidates[0]["name"] if candidates else "N/A"
    top_score = candidates[0]["fit_score"] if candidates else 0.0
    logger.info(
        f"Completed TypeSafe batch screening for '{job_role}' in {elapsed:.2f}s: "
        f"Evaluated={len(candidates)}/{len(resumes)}, Selected={selected_count}, "
        f"AvgScore={avg_score}%, TopCandidate='{top_name}' ({top_score}%), "
        f"TargetSeniority='{job_profile.seniority_label}' (Score={job_profile.seniority_score:.2f})"
    )

    role_weights = {
        "technical": 0.25,
        "seniority": 0.20,
        "experience": 0.20,
        "domain": 0.15,
        "requirements": 0.15,
        "education": 0.05,
    }

    return {
        "success": True,
        "job_role": job_profile.role_title,
        "seniority_tier": job_profile.seniority_label.lower()
        .replace(" ", "_")
        .replace("/", "_"),
        "seniority_label": job_profile.seniority_label,
        "role_weights": role_weights,
        "total_evaluated": len(candidates),
        "top_3_shortlisted": min(3, len(candidates)),
        "top_5_shortlisted": min(5, len(candidates)),
        "selected_candidates_count": selected_count,
        "average_fit_score": avg_score,
        "latency_seconds": round(elapsed, 2),
        "candidates": candidates,
    }


class EnterpriseScreeningService:
    """Service facade for enterprise bulk screening operations."""

    screen_resumes_batch = staticmethod(screen_resumes_batch)
    run_bulk_screening = staticmethod(screen_resumes_batch)
    validate_screening_batch = staticmethod(validate_screening_batch)


run_bulk_screening = screen_resumes_batch

__all__ = [
    "EnterpriseScreeningService",
    "screen_resumes_batch",
    "run_bulk_screening",
    "validate_screening_batch",
]
