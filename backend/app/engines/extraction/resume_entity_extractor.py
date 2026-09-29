"""
CareerLens AI - Resume Entity Extractor
Extracts candidate identity, contact details, section texts, and timeline spans.
"""

from __future__ import annotations

import re
import datetime
from typing import Any, Dict, List, Optional
from app.models.domain.candidate import ResumeBlock


def extract_candidate_name(header_lines: List[str]) -> str:
    """
    Identifies candidate name from early header lines using heuristics:
    2-4 words, alphabetic, title-cased, not containing contact cues.
    """
    contact_cues = [
        "email",
        "phone",
        "linkedin",
        "github",
        "curriculum",
        "resume",
        "cv",
        "portfolio",
        "address",
        "http",
        "@",
        "+",
        "page",
        "developer",
        "engineer",
    ]
    for line in header_lines[:5]:
        stripped = line.strip()
        lower = stripped.lower()
        if any(cue in lower for cue in contact_cues):
            continue

        words = stripped.split()
        if 2 <= len(words) <= 4:
            if all(re.match(r"^[A-Z][a-zA-Z\.\-]*$", w) for w in words):
                return stripped

    if header_lines:
        first_clean = header_lines[0].strip()
        if 2 <= len(first_clean) <= 40 and not any(
            c in first_clean.lower() for c in contact_cues[:5]
        ):
            return first_clean

    return "Candidate"


def extract_contact_info(
    text: str, hyperlinks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Extracts email, phone, and professional links (LinkedIn, GitHub)."""
    email_match = re.search(r"[\w\.\+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group(0) if email_match else None

    phone_patterns = [
        r"(?:\+91[\s\-]?)?[6-9]\d{9}",  # Indian 10-digit
        r"(?:\+91[\s\-]?)?[6-9]\d{4}[\s\-]?\d{5}",  # Indian 5+5
        r"(?:\+?1[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}",  # US
    ]
    phone = None
    for pat in phone_patterns:
        pm = re.search(pat, text)
        if pm:
            phone = pm.group(0).strip()
            break

    all_links = list(hyperlinks or [])
    url_matches = re.findall(r"https?://[^\s\,\;\)\>]+", text)
    for u in url_matches:
        if u not in all_links:
            all_links.append(u)

    linkedin = next((u for u in all_links if "linkedin.com" in u.lower()), None)
    github = next((u for u in all_links if "github.com" in u.lower()), None)

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "all_urls": all_links,
    }


def estimate_experience_years_span(experience_text: str) -> float:
    """Calculates calendar year span from date mentions (e.g. 2019 - 2024)."""
    current_year = datetime.datetime.now().year
    years_found = [int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", experience_text)]
    if not years_found:
        return 0.0

    valid_years = [y for y in years_found if 1990 <= y <= current_year]
    if not valid_years:
        return 0.0

    return float(max(0, current_year - min(valid_years)))


def aggregate_sections_from_blocks(blocks: List[ResumeBlock]) -> Dict[str, str]:
    """Groups text of blocks by their assigned section."""
    sections: Dict[str, List[str]] = {}
    for b in blocks:
        sec = b.section_assigned or b.section_candidate or "other"
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(b.text)

    return {k: "\n\n".join(v).strip() for k, v in sections.items()}
