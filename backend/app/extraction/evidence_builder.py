"""
CareerLens AI - Evidence Builder
Preserves verbatim resume snippets and maps atomic claims to source ResumeBlock instances.
"""

from __future__ import annotations

import re
from typing import Dict, List
from app.models.candidate_profile import ResumeBlock
from app.models.evidence import Evidence
from app.tools.tech_keyword_extractor import extract_tech_keywords


def build_evidence_from_blocks(blocks: List[ResumeBlock]) -> List[Evidence]:
    """
    Decomposes resume blocks (especially experience and project blocks) into
    traceable Evidence instances with associated technology tags.
    """
    evidences: List[Evidence] = []
    evidence_idx = 100

    for block in blocks:
        section = block.section_assigned or block.section_candidate or "other"
        # Split block text by bullet points or sentence breaks
        lines = block.text.splitlines()
        for line in lines:
            line_str = line.strip()
            # Ignore very short lines (under 15 chars) that lack substantive context
            if len(line_str) < 15:
                continue

            extracted = extract_tech_keywords(line_str)
            skills = extracted.get("extracted_skills", [])

            evidences.append(Evidence(
                evidence_id=f"E{evidence_idx}",
                source_block_id=block.id,
                section=section,
                text=line_str,
                skills_mentioned=skills,
            ))
            evidence_idx += 1

    return evidences


def find_evidence_for_requirement(requirement: str, evidences: List[Evidence]) -> List[Evidence]:
    """
    Retrieves candidate evidence snippets relevant to a specific JD requirement.
    Uses symbol-aware case-insensitive substring and skill matching.
    """
    req_lower = requirement.lower().strip()
    req_words = [w for w in re.findall(r"\w+", req_lower) if len(w) > 2]
    matched: List[Evidence] = []

    for ev in evidences:
        ev_lower = ev.text.lower()
        # Direct skill match
        if any(req_lower == s.lower() for s in ev.skills_mentioned):
            matched.append(ev)
            continue

        # Substring match
        if req_lower in ev_lower:
            matched.append(ev)
            continue

        # Word overlap
        if req_words and all(w in ev_lower for w in req_words):
            matched.append(ev)

    return matched
