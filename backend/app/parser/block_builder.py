"""
CareerLens AI - Resume Block Builder
Segments document into discrete ResumeBlock instances with spatial and section metadata.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from app.models.candidate_profile import ResumeBlock


SECTION_TAXONOMY: Dict[str, List[str]] = {
    "summary": [
        "summary", "professional summary", "executive summary", "profile",
        "professional profile", "career summary", "about me", "overview",
        "career objective", "objective", "personal statement"
    ],
    "experience": [
        "experience", "work experience", "employment history", "professional experience",
        "work history", "career history", "relevant experience", "practical experience",
        "industry experience", "internship experience", "internships", "employment"
    ],
    "education": [
        "education", "academic background", "academic qualifications", "academics",
        "educational background", "degrees", "qualifications", "education & credentials",
        "university", "academic record"
    ],
    "technical": [
        "skills", "technical skills", "skills & tools", "technologies",
        "core competencies", "technical proficiencies", "tools & technologies",
        "programming skills", "technical expertise", "stack"
    ],
    "projects": [
        "projects", "personal projects", "key projects", "academic projects",
        "selected projects", "technical projects", "open source"
    ],
    "certifications": [
        "certifications", "licenses & certifications", "certificates",
        "credentials", "courses", "professional certifications"
    ],
}


def classify_section_header(
    line: str,
    font_size: Optional[float] = None,
    is_bold: bool = False,
    median_font_size: Optional[float] = None,
) -> Tuple[Optional[str], float]:
    """
    Determines if a given text line represents a section header.
    Returns (canonical_section_name, confidence) or (None, 0.0).
    """
    clean = re.sub(r"[:\-\|\#\*\_\~\>\•]", " ", line).strip()
    clean_lower = clean.lower()

    if not clean_lower or len(clean_lower) > 50:
        return None, 0.0

    matched_section: Optional[str] = None
    for section_name, synonyms in SECTION_TAXONOMY.items():
        for syn in synonyms:
            if clean_lower == syn:
                matched_section = section_name
                break
            if clean_lower.startswith(syn + " ") or clean_lower.endswith(" " + syn):
                matched_section = section_name
                break
        if matched_section:
            break

    if not matched_section:
        return None, 0.0

    confidence = 0.60
    if median_font_size and font_size and font_size > median_font_size * 1.05:
        confidence += 0.20
    if is_bold:
        confidence += 0.15
    if line.isupper() and len(line) > 3:
        confidence += 0.05

    return matched_section, min(1.0, confidence)


def assemble_blocks_from_lines(page_lines: List[List[Dict[str, Any]]], median_font: float) -> List[ResumeBlock]:
    """
    Transforms extracted per-page line items into contiguous ResumeBlock objects.
    """
    blocks: List[ResumeBlock] = []
    block_counter = 1
    current_section = "summary"
    current_lines: List[str] = []
    current_page = 1
    current_font = median_font
    current_bold = False
    current_y = 0.0

    for page_idx, lines in enumerate(page_lines):
        page_num = page_idx + 1
        for l in lines:
            text = l.get("text", "").strip()
            if not text:
                continue

            font_size = float(l.get("font_size", median_font))
            is_bold = bool(l.get("is_bold", False))
            y_pos = float(l.get("y_pos", 0.0))

            section_hdr, conf = classify_section_header(
                text, font_size=font_size, is_bold=is_bold, median_font_size=median_font
            )

            if section_hdr:
                # Flush previous block
                if current_lines:
                    blocks.append(ResumeBlock(
                        id=f"b{block_counter}",
                        page=current_page,
                        text="\n".join(current_lines),
                        font_size=current_font,
                        is_bold=current_bold,
                        y_pos=current_y,
                        section_candidate=current_section,
                        section_assigned=current_section,
                    ))
                    block_counter += 1
                    current_lines = []

                current_section = section_hdr
                current_page = page_num
                current_font = font_size
                current_bold = is_bold
                current_y = y_pos
            else:
                if not current_lines:
                    current_page = page_num
                    current_font = font_size
                    current_bold = is_bold
                    current_y = y_pos
                current_lines.append(text)

    # Flush final block
    if current_lines:
        blocks.append(ResumeBlock(
            id=f"b{block_counter}",
            page=current_page,
            text="\n".join(current_lines),
            font_size=current_font,
            is_bold=current_bold,
            y_pos=current_y,
            section_candidate=current_section,
            section_assigned=current_section,
        ))

    return blocks
