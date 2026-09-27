"""
CareerLens AI - Deterministic Resume Parser (Backward-Compatibility Shim)

Re-exports resume parsing functions and taxonomies from app.parsers.resume_parser.
"""

from __future__ import annotations

from app.parsers.resume_parser import (
    SECTION_TAXONOMY,
    clean_cid_artifacts,
    classify_section_header,
    detect_column_split,
    extract_candidate_name,
    extract_contact_info,
    parse_resume_from_pdf,
    parse_resume_from_text,
)

# Aliases
parse_pdf_resume_deterministically = parse_resume_from_pdf
parse_text_resume_deterministically = parse_resume_from_text
parse_resume_deterministically = parse_resume_from_pdf

__all__ = [
    "SECTION_TAXONOMY",
    "clean_cid_artifacts",
    "classify_section_header",
    "detect_column_split",
    "extract_candidate_name",
    "extract_contact_info",
    "parse_resume_from_pdf",
    "parse_resume_from_text",
    "parse_pdf_resume_deterministically",
    "parse_text_resume_deterministically",
    "parse_resume_deterministically",
]
