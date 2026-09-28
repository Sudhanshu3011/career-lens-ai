"""
CareerLens AI - Entity Extraction and Normalization Package
"""

from app.extraction.jd_extractor import extract_job_profile
from app.extraction.resume_entity_extractor import (
    extract_candidate_name,
    extract_contact_info,
    estimate_experience_years_span,
    aggregate_sections_from_blocks,
)
from app.extraction.evidence_builder import build_evidence_from_blocks, find_evidence_for_requirement

__all__ = [
    "extract_job_profile",
    "extract_candidate_name",
    "extract_contact_info",
    "estimate_experience_years_span",
    "aggregate_sections_from_blocks",
    "build_evidence_from_blocks",
    "find_evidence_for_requirement",
]
