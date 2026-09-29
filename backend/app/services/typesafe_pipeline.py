"""
CareerLens AI - TypeSafe System One Screening Pipeline
Executes modular requirement-evidence-judgment candidate screening with Jev primitives.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from app.models.domain.job import JobProfile
from app.models.domain.candidate import CandidateProfile
from app.models.domain.decision import DecisionState
from app.models.domain.evidence import Evidence
from app.engines.parser.pdf_parser import parse_pdf_to_blocks
from app.engines.extraction.resume_entity_extractor import (
    extract_candidate_name,
    extract_contact_info,
    estimate_experience_years_span,
    aggregate_sections_from_blocks,
)
from app.engines.extraction.evidence_builder import build_evidence_from_blocks
from app.engines.jev.client import jev_client
from app.engines.laya.client import laya_client
from app.engines.jev.questions import build_candidate_seniority_question
from app.engines.jev.rubric import seniority_score_to_label
from app.engines.evaluation.seniority_evaluator import evaluate_seniority_gap
from app.engines.evaluation.requirement_matcher import evaluate_candidate_requirements
from app.engines.evaluation.composite_score import calculate_composite_decision
from app.utils.report_builder import build_candidate_enterprise_record
from app.engines.extraction.tech_keywords import (
    extract_tech_keywords,
    expand_with_parent_domains,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


def _extract_candidate_components(pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Deterministically segments PDF layout and extracts candidate identity, contact,
    and textual sections.
    """
    blocks, hyperlinks, raw_text, header_lines = parse_pdf_to_blocks(pdf_bytes)
    candidate_name = extract_candidate_name(header_lines)
    if not candidate_name or candidate_name.lower() in ("candidate", "unknown"):
        clean_filename = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
        candidate_name = clean_filename.title()

    contact_info = extract_contact_info(raw_text, hyperlinks)
    sections = aggregate_sections_from_blocks(blocks)
    summary_text = sections.get("summary", "")
    exp_text = sections.get("experience", "")
    edu_text = sections.get("education", "")

    if not exp_text and not summary_text:
        exp_text = raw_text[:2000]

    span_years = estimate_experience_years_span(exp_text)

    return {
        "blocks": blocks,
        "raw_text": raw_text,
        "candidate_name": candidate_name,
        "contact_info": contact_info,
        "sections": sections,
        "summary_text": summary_text,
        "exp_text": exp_text,
        "edu_text": edu_text,
        "span_years": span_years,
    }


def _compute_technical_overlap(
    raw_text: str, required_skills: List[str]
) -> Tuple[Dict[str, Any], List[str], List[str], List[str], float]:
    """
    Extracts skills, tools, and domains, and computes ontology-expanded technical overlap.
    """
    tech_data = extract_tech_keywords(raw_text)
    cand_skills: List[str] = tech_data.get("extracted_skills", [])
    skills_by_domain = tech_data.get("skills_by_domain", {})
    tools = (
        skills_by_domain.get("DevOps & Cloud", [])
        + skills_by_domain.get("Big Data & Distributed Computing", [])
        + skills_by_domain.get("Databases & Storage", [])
    )
    domains = list(skills_by_domain.keys())

    cand_skills_expanded = expand_with_parent_domains(cand_skills)
    jd_skills_expanded = expand_with_parent_domains(required_skills)

    cand_lower = {s.lower(): s for s in cand_skills_expanded}
    jd_lower = {s.lower(): s for s in jd_skills_expanded}
    matched_skills = [jd_lower[k] for k in jd_lower if k in cand_lower]
    missing_skills = [jd_lower[k] for k in jd_lower if k not in cand_lower]
    bonus_skills = [cand_lower[k] for k in cand_lower if k not in jd_lower]

    tech_overlap_pct = (
        round((len(matched_skills) / max(1, len(jd_skills_expanded))) * 100.0, 1)
        if jd_skills_expanded
        else 100.0
    )

    technical_overlap = {
        "jd_skills_required": required_skills,
        "matched_skills": matched_skills,
        "missing_jd_skills": missing_skills,
        "candidate_bonus_skills": bonus_skills,
        "skill_overlap_percentage": tech_overlap_pct,
    }

    return technical_overlap, cand_skills, tools, domains, tech_overlap_pct


def _build_hard_gate_rejection_record(
    idx: int,
    filename: str,
    candidate_name: str,
    tech_overlap_pct: float,
    technical_overlap: Dict[str, Any],
    cand_skills: List[str],
    tools: List[str],
    domains: List[str],
    sections_info: Dict[str, Any],
) -> Dict[str, Any]:
    """Builds immediate rejection record when the candidate fails the hard technical gate."""
    matched = technical_overlap.get("matched_skills", [])
    missing = technical_overlap.get("missing_jd_skills", [])
    rejection_msg = (
        f"Candidate's technical skills ({tech_overlap_pct}% overlap) do not meet the "
        f"minimum threshold for this role. "
        f"Matched: {matched or ['none']}. "
        f"Required but missing: {missing[:6]}."
    )
    return {
        "candidate_id": f"cand-{idx + 1}",
        "name": candidate_name,
        "filename": filename,
        "fit_score": 0.0,
        "raw_score": 0.0,
        "decision": "REJECT",
        "rejection_reason": "does_not_fit_role",
        "rejection_message": rejection_msg,
        "seniority_tier": "mid_level",
        "seniority_label": "Mid-Level",
        "target_seniority_tier": "mid_level",
        "target_seniority_label": "Mid-Level",
        "candidate_seniority_tier": "mid_level",
        "candidate_seniority_label": "Mid-Level",
        "seniority_alignment": "ALIGNED",
        "role_weights": {},
        "high_hits_count": 0,
        "raw_weighted_probability": 0.0,
        "penalty_applied": 0.0,
        "total_weighted_probability": 0.0,
        "breakdown": {
            "technical_requirements": round(tech_overlap_pct, 1),
            "experience_requirements": 0,
            "domain_alignment": 0,
            "education_alignment": 0,
            "evidence_strength": 0,
        },
        "parameter_evaluations": {},
        "skills": cand_skills,
        "tools": tools,
        "domains": domains,
        "decision_reason": rejection_msg,
        "technical_overlap": technical_overlap,
        "inspection": {
            "summary": sections_info.get("summary_text", ""),
            "experience": sections_info.get("exp_text", ""),
            "education": sections_info.get("edu_text", ""),
            "skills": ", ".join(cand_skills),
            "contact_info": sections_info.get("contact_info", {}),
        },
    }


def _evaluate_seniority_primitive(
    pipeline_mode: str,
    exp_text: str,
    summary_text: str,
    edu_text: str,
) -> Tuple[float, float, str]:
    """Executes atomic Score primitive for candidate seniority using selected pipeline."""
    sen_state = {
        "text": (
            f"Candidate Work Experience:\n{exp_text or 'No professional experience listed (student/fresher profile).'}\n\n"
            f"Summary:\n{summary_text or 'None'}\n\n"
            f"Education:\n{edu_text or 'None'}"
        )
    }
    sen_question = build_candidate_seniority_question()
    client = laya_client if pipeline_mode == "laya_local" else jev_client
    sen_answers = client.predict(sen_state, sen_question)
    cand_sen_ans = sen_answers.get("candidate_seniority", {})

    cand_sen_score = float(cand_sen_ans.get("score", 1.0))
    cand_sen_conf = float(cand_sen_ans.get("confidence", 0.75))
    cand_sen_label = seniority_score_to_label(cand_sen_score)
    return cand_sen_score, cand_sen_conf, cand_sen_label


def _evaluate_requirements_and_decision(
    job_profile: JobProfile,
    candidate_profile: CandidateProfile,
    evidences: List[Evidence],
    pipeline_mode: str,
    cand_sen_score: float,
    cand_sen_conf: float,
    tech_overlap_pct: float,
    domains: List[str],
    edu_text: str,
    idx: int,
) -> DecisionState:
    """Evaluates candidate requirements, seniority delta, and composite decision state."""
    assessments, hard_gates, all_gates_passed = evaluate_candidate_requirements(
        job_profile=job_profile,
        candidate_profile=candidate_profile,
        evidences=evidences,
        pipeline_mode=pipeline_mode,
    )

    seniority_assessment = evaluate_seniority_gap(
        jd_score=job_profile.seniority_score,
        candidate_score=cand_sen_score,
        confidence=cand_sen_conf,
    )

    domain_overlap_pct = 80.0 if any(d in job_profile.domain for d in domains) else 40.0
    has_education = bool(edu_text and len(edu_text) > 20)

    return calculate_composite_decision(
        candidate_id=f"cand-{idx + 1}",
        candidate_name=candidate_profile.candidate_name,
        seniority=seniority_assessment,
        assessments=assessments,
        hard_gates=hard_gates,
        all_hard_gates_passed=all_gates_passed,
        technical_overlap_pct=tech_overlap_pct,
        domain_overlap_pct=domain_overlap_pct,
        has_education=has_education,
    )


def evaluate_candidate_typesafe(
    pdf_bytes: bytes,
    filename: str,
    job_profile: JobProfile,
    idx: int,
    pipeline_mode: str = "typesafe",
) -> Dict[str, Any]:
    """
    Executes end-to-end decomposed TypeSafe evaluation for a single resume PDF:
    1. Deterministic PDF Layout & Spatial Block Segmentation.
    2. Candidate Identity & Timeline Extraction.
    3. Technical Competency Overlap & Hard Gate Check (<20%).
    4. Jev/Laya Seniority Judgment (Score primitive, 0.0 to 6.0).
    5. Requirement Evidence Judgment (Noul & Score primitives).
    6. Deterministic Decision Aggregation & Structured Report Generation.
    """
    start_time = time.perf_counter()

    # 1. Parse PDF layout and extract components
    comp = _extract_candidate_components(pdf_bytes, filename)

    # 2. Compute technical skills overlap
    tech_overlap, cand_skills, tools, domains, tech_overlap_pct = (
        _compute_technical_overlap(
            raw_text=comp["raw_text"],
            required_skills=job_profile.required_skills,
        )
    )

    # 3. Hard technical gate (<20% overlap -> immediate reject)
    if tech_overlap_pct < 20.0:
        logger.info(
            "Hard technical gate triggered for '%s' (%s): overlap=%.1f%%",
            comp["candidate_name"],
            filename,
            tech_overlap_pct,
        )
        return _build_hard_gate_rejection_record(
            idx=idx,
            filename=filename,
            candidate_name=comp["candidate_name"],
            tech_overlap_pct=tech_overlap_pct,
            technical_overlap=tech_overlap,
            cand_skills=cand_skills,
            tools=tools,
            domains=domains,
            sections_info=comp,
        )

    # 4. Seniority Judgment primitive (Score)
    sen_score, sen_conf, sen_label = _evaluate_seniority_primitive(
        pipeline_mode=pipeline_mode,
        exp_text=comp["exp_text"],
        summary_text=comp["summary_text"],
        edu_text=comp["edu_text"],
    )

    # 5. Build candidate profile
    candidate_profile = CandidateProfile(
        candidate_name=comp["candidate_name"],
        email=comp["contact_info"].get("email"),
        phone=comp["contact_info"].get("phone"),
        hyperlinks=comp["contact_info"].get("all_urls", []),
        seniority_score=round(sen_score, 2),
        seniority_confidence=round(sen_conf, 2),
        seniority_label=sen_label,
        blocks=comp["blocks"],
        sections=comp["sections"],
        technical_skills=cand_skills,
        tools=tools,
        domains=domains,
        experience_years_span=comp["span_years"],
        summary_text=comp["summary_text"],
        experience_text=comp["exp_text"],
        education_text=comp["edu_text"],
        raw_text=comp["raw_text"],
    )

    # 6. Evaluate requirements and composite decision
    evidences = build_evidence_from_blocks(comp["blocks"])
    decision_state = _evaluate_requirements_and_decision(
        job_profile=job_profile,
        candidate_profile=candidate_profile,
        evidences=evidences,
        pipeline_mode=pipeline_mode,
        cand_sen_score=sen_score,
        cand_sen_conf=sen_conf,
        tech_overlap_pct=tech_overlap_pct,
        domains=domains,
        edu_text=comp["edu_text"],
        idx=idx,
    )

    # 7. Assemble enterprise response record
    record = build_candidate_enterprise_record(
        idx=idx,
        filename=filename,
        candidate=candidate_profile,
        job=job_profile,
        decision_state=decision_state,
        technical_overlap=tech_overlap,
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        f"TypeSafe Candidate Screened [{idx+1}]: '{comp['candidate_name']}' ({filename}) in {elapsed_ms:.1f}ms -> "
        f"Fit={record['fit_score']}%, Decision={record['decision']}, HardGatesPassed={decision_state.hard_gates_passed}, "
        f"Seniority={sen_label} vs Target={job_profile.seniority_label}"
    )

    return record
