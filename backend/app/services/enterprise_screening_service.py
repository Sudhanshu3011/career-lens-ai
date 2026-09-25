"""
CareerLens AI - Enterprise Bulk Resume Screening Service

Business logic for batch candidate evaluation, multi-dimensional scoring,
concurrent async processing, and Top 3 candidate ranking.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List
from fastapi import HTTPException, UploadFile, status

from app.tools.deterministic_parser import parse_resume_from_pdf
from app.tools.candidate_scorer import score_resume_against_jd
from app.core.decision_engine import decision_engine
from app.core.logger import get_logger

logger = get_logger(__name__)

VALID_PDF_MIME_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/acrobat",
    "applications/vnd.pdf",
    "text/pdf",
}


def validate_screening_batch(resumes: List[UploadFile]) -> None:
    """
    Validates batch constraints and verifies that every uploaded file is a PDF
    by both filename extension and MIME type.
    """
    if not resumes:
        logger.warning("Batch validation failed: No resume files provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume files provided. Please upload at least 1 PDF resume.",
        )

    if len(resumes) > 15:
        logger.warning(f"Batch validation failed: {len(resumes)} resumes uploaded (max 15 allowed)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum 15 resumes allowed per batch. You uploaded {len(resumes)}.",
        )

    for file in resumes:
        filename = (file.filename or "").strip()
        if not filename.lower().endswith(".pdf"):
            logger.warning(f"Batch validation failed: file '{filename}' lacks .pdf extension")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{filename or 'unnamed'}' is not a PDF. All resumes must have a .pdf extension.",
            )

        content_type = (file.content_type or "").split(";")[0].strip().lower()
        if content_type not in VALID_PDF_MIME_TYPES and content_type != "application/octet-stream":
            logger.warning(f"Batch validation failed: file '{filename}' has invalid MIME type '{file.content_type}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File '{filename}' has invalid MIME type '{file.content_type}'. "
                    "All uploaded files must have a valid PDF MIME type ('application/pdf')."
                ),
            )
    logger.info(f"Validated screening batch containing {len(resumes)} valid PDF file(s)")


def _map_decision(overall_decision: str) -> str:
    """Maps decision engine verdict to standard enterprise decision categories."""
    upper_verdict = overall_decision.upper()
    if "SELECT" in upper_verdict or "STRONG" in upper_verdict:
        return "SELECT"
    if "REJECT" in upper_verdict or "WEAK" in upper_verdict or "POOR" in upper_verdict:
        return "REJECT"
    return "BORDERLINE"


def _build_candidate_record(
    idx: int,
    filename: str,
    parsed_data: Dict[str, Any],
    scoring_res: Dict[str, Any],
) -> Dict[str, Any]:
    """Assembles a scored candidate record with dimension breakdowns and overlap analysis."""
    candidate_name = parsed_data.get("candidate_name")
    if not candidate_name or candidate_name.lower() in ("candidate", "unknown"):
        clean_filename = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
        candidate_name = clean_filename.title()

    fit_score_raw = scoring_res.get("final_score", 0.0)
    fit_score_pct = scoring_res.get("fit_score", round(fit_score_raw * 10, 1))
    breakdown = scoring_res.get("breakdown", {})
    tech_overlap = scoring_res.get("technical_overlap", {})
    decision = _map_decision(scoring_res.get("overall_decision", "BORDERLINE"))

    target_tier = scoring_res.get("target_seniority_tier", scoring_res.get("seniority_tier", "mid_level"))
    target_label = scoring_res.get("target_seniority_label", scoring_res.get("seniority_label", "Mid-Level"))
    cand_tier = scoring_res.get("candidate_seniority_tier", "mid_level")
    cand_label = scoring_res.get("candidate_seniority_label", "Mid-Level")

    if cand_tier == target_tier:
        seniority_alignment = "ALIGNED"
        alignment_note = f"Candidate seniority ({cand_label}) matches target requisition."
    elif (cand_tier == "beginner" and target_tier in ("mid_level", "senior")) or (cand_tier == "mid_level" and target_tier == "senior"):
        seniority_alignment = "GAP"
        alignment_note = f"Seniority gap: Candidate is {cand_label} applying for a {target_label} position."
    else:
        seniority_alignment = "EXCEEDS"
        alignment_note = f"Candidate seniority ({cand_label}) exceeds {target_label} requisition."

    role_weights = scoring_res.get("role_weights", {})
    high_hits_count = scoring_res.get("high_hits_count", 0)
    raw_weighted_prob = scoring_res.get("raw_weighted_probability", 0.0)
    penalty_applied = scoring_res.get("penalty_applied", 0.0)
    total_weighted_prob = scoring_res.get("total_weighted_probability", 0.0)

    matched = tech_overlap.get("matched_skills", [])
    missing = tech_overlap.get("missing_jd_skills", [])
    matched_str = f"Strong alignment in {', '.join(matched[:3])}." if matched else "Limited direct tech matches."
    gap_str = f" Missing requirements: {', '.join(missing[:3])}." if missing else " No critical skill deficits identified."
    penalty_str = f" (Penalty applied: -{penalty_applied*100:.0f}%)" if penalty_applied > 0 else " (No penalty applied)"
    decision_reason = (
        f"Candidate ({cand_label}) achieved {fit_score_pct}% match for {target_label} requisition. "
        f"Hit dominant High rating in {high_hits_count}/5 dimensions{penalty_str}. "
        f"{alignment_note} {matched_str}{gap_str}"
    )

    tools = (
        parsed_data.get("skills_by_domain", {}).get("DevOps & Cloud", [])
        + parsed_data.get("skills_by_domain", {}).get("Big Data & Distributed Computing", [])
    )

    return {
        "candidate_id": f"cand-{idx + 1}",
        "name": candidate_name,
        "filename": filename,
        "fit_score": fit_score_pct,
        "raw_score": round(fit_score_raw, 1),
        "decision": decision,
        "seniority_tier": cand_tier,
        "seniority_label": cand_label,
        "target_seniority_tier": target_tier,
        "target_seniority_label": target_label,
        "candidate_seniority_tier": cand_tier,
        "candidate_seniority_label": cand_label,
        "seniority_alignment": seniority_alignment,
        "role_weights": role_weights,
        "high_hits_count": high_hits_count,
        "raw_weighted_probability": raw_weighted_prob,
        "penalty_applied": penalty_applied,
        "total_weighted_probability": total_weighted_prob,
        "breakdown": {
            "technical_requirements": breakdown.get("technical_requirements", 0),
            "experience_requirements": breakdown.get("experience_requirements", 0),
            "domain_alignment": breakdown.get("domain_alignment", 0),
            "education_alignment": breakdown.get("education_alignment", 70),
            "evidence_strength": breakdown.get("evidence_strength", 0),
        },
        "parameter_evaluations": scoring_res.get("parameter_evaluations", {}),
        "skills": parsed_data.get("tech_skills", []),
        "tools": tools,
        "domains": list(parsed_data.get("skills_by_domain", {}).keys()),
        "decision_reason": decision_reason,
        "technical_overlap": {
            "matched_skills": tech_overlap.get("matched_skills", []),
            "missing_jd_skills": tech_overlap.get("missing_jd_skills", []),
            "candidate_bonus_skills": tech_overlap.get("candidate_bonus_skills", []),
            "skill_overlap_percentage": tech_overlap.get("skill_overlap_percentage", 0.0),
        },
        "inspection": {
            "summary": parsed_data.get("summary", ""),
            "experience": parsed_data.get("experience", ""),
            "education": parsed_data.get("education", ""),
            "skills": parsed_data.get("skills", ""),
            "contact_info": parsed_data.get("contact_info", {}),
        },
    }


def _build_fallback_record(idx: int, filename: str, error_message: str) -> Dict[str, Any]:
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
    combined_jd: str,
    idx: int,
    job_role: str = "",
) -> Dict[str, Any] | None:
    """
    Asynchronously reads and evaluates a single resume file.
    Offloads synchronous CPU-bound parsing and scoring to worker threads.
    """
    filename = file.filename or f"resume_{idx+1}.pdf"
    cand_start = time.perf_counter()
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes or len(pdf_bytes) < 100:
            logger.warning(f"Skipping empty or corrupt PDF resume: {filename} ({len(pdf_bytes) if pdf_bytes else 0} bytes)")
            return None

        logger.info(f"Processing candidate file [{idx+1}]: {filename} ({len(pdf_bytes)} bytes)")
        parsed_data = await asyncio.to_thread(parse_resume_from_pdf, pdf_bytes)
        scoring_res = await asyncio.to_thread(
            score_resume_against_jd,
            resume_data=parsed_data,
            job_description=combined_jd,
            job_role=job_role,
        )

        record = _build_candidate_record(idx, filename, parsed_data, scoring_res)
        cand_elapsed = (time.perf_counter() - cand_start) * 1000
        logger.info(
            f"Candidate evaluated [{idx+1}]: '{record['name']}' ({filename}) in {cand_elapsed:.1f}ms "
            f"-> Fit={record['fit_score']}%, Decision={record['decision']}, "
            f"CandSeniority={record['candidate_seniority_label']} vs Target={record['target_seniority_label']}"
        )
        return record

    except Exception as exc:
        logger.error(f"Failed to process candidate {filename}: {exc}", exc_info=True)
        return _build_fallback_record(idx, filename, str(exc))


def _rank_and_flag_candidates(candidates: List[Dict[str, Any]]) -> None:
    """Sorts candidates descending by unified total weighted probability and assigns rank badges."""
    candidates.sort(
        key=lambda c: (c.get("total_weighted_probability", 0.0), c.get("fit_score", 0.0)),
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
) -> Dict[str, Any]:
    """
    Executes concurrent batch screening of resumes against the target job description.
    Uses asyncio.gather for parallel async execution across uploaded files.
    """
    validate_screening_batch(resumes)

    start_time = time.perf_counter()
    logger.info(
        f"Starting batch screening pipeline: Role='{job_role}', "
        f"BatchSize={len(resumes)}, JDLength={len(job_description)} chars"
    )
    combined_jd = f"Target Role: {job_role}\n\nJob Requirements:\n{job_description}"

    # Process all candidates concurrently with asyncio.gather
    evaluation_tasks = [
        _evaluate_single_candidate(file=file, combined_jd=combined_jd, idx=idx, job_role=job_role)
        for idx, file in enumerate(resumes)
    ]
    raw_results = await asyncio.gather(*evaluation_tasks)
    candidates = [res for res in raw_results if res is not None]

    _rank_and_flag_candidates(candidates)

    elapsed = time.perf_counter() - start_time
    avg_score = (
        round(sum(c["fit_score"] for c in candidates) / len(candidates), 1)
        if candidates
        else 0.0
    )
    selected_count = sum(1 for c in candidates if c["decision"] == "SELECT")

    # Classify JD seniority tier and active weights for the batch
    try:
        jd_res = decision_engine.classify_jd_seniority(combined_jd, job_role=job_role)
        tier = jd_res["seniority_tier"]
        label = jd_res["seniority_label"]
        weights = jd_res["weights"]
    except Exception:
        tier, label, weights = "mid_level", "Mid-Level", {
            "technical": 0.25, "experience": 0.30, "domain": 0.20, "education": 0.05, "evidence": 0.20
        }

    top_name = candidates[0]["name"] if candidates else "N/A"
    top_score = candidates[0]["fit_score"] if candidates else 0.0
    logger.info(
        f"Completed batch screening for '{job_role}' in {elapsed:.2f}s: "
        f"Evaluated={len(candidates)}/{len(resumes)}, Selected={selected_count}, "
        f"AvgScore={avg_score}%, TopCandidate='{top_name}' ({top_score}%), "
        f"TargetSeniority='{label}'"
    )

    return {
        "success": True,
        "job_role": job_role,
        "seniority_tier": tier,
        "seniority_label": label,
        "role_weights": weights,
        "total_evaluated": len(candidates),
        "top_3_shortlisted": min(3, len(candidates)),
        "top_5_shortlisted": min(5, len(candidates)),
        "selected_candidates_count": selected_count,
        "average_fit_score": avg_score,
        "latency_seconds": round(elapsed, 2),
        "candidates": candidates,
    }
