"""
CareerLens AI - Deterministic Resume Section Parser (Zero-LLM)

A standalone, non-autoregressive resume section parser that segments
PDF and plain-text resumes into structured sections without making any LLM calls.

Techniques:
1. Spatial & Typography Analysis (via pdfplumber text lines & font metadata).
2. Embedded PDF Annotation Extraction: Hyperlinks for LinkedIn, GitHub, Portfolio.
3. Section Ontology & Taxonomy matching: standard synonym dictionary.
4. Finite State Machine (FSM): streaming boundary segmentation.
5. Deterministic Identity & Contact extraction: Regex for email, phone, URLs, name.
"""

from __future__ import annotations

import io
import re
import statistics
from typing import Any, Dict, List, Optional, Tuple
import pdfplumber

from app.core.logger import get_logger
from app.tools.tech_keyword_extractor import extract_tech_keywords

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# 1. Section Taxonomy / Canonical Ontology
# ---------------------------------------------------------------------------

SECTION_TAXONOMY: dict[str, list[str]] = {
    "summary": [
        "summary",
        "professional summary",
        "executive summary",
        "profile",
        "professional profile",
        "career summary",
        "about me",
        "overview",
        "career objective",
        "objective",
        "personal statement",
        "biography",
        "bio",
    ],
    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
        "work history",
        "career history",
        "relevant experience",
        "practical experience",
        "industry experience",
        "internship experience",
        "internships",
        "employment",
        "positions held",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "academics",
        "educational background",
        "degrees",
        "qualifications",
        "education & credentials",
        "education and training",
        "university",
        "academic record",
        "academic profile",
        "education profile",
        "examination",
        "examinations",
    ],
    "skills": [
        "skills",
        "technical skills",
        "skills & tools",
        "skills and tools",
        "technologies",
        "core competencies",
        "technical proficiencies",
        "areas of expertise",
        "competencies",
        "tools & technologies",
        "key skills",
        "expertise",
        "technical expertise",
        "programming skills",
        "stack",
    ],
    "projects": [
        "projects",
        "personal projects",
        "key projects",
        "academic projects",
        "technical projects",
        "selected projects",
        "portfolio projects",
        "project experience",
        "notable projects",
        "open source projects",
    ],
    "certifications": [
        "certifications",
        "licenses & certifications",
        "licenses and certifications",
        "certificates",
        "credentials",
        "licenses",
        "certifications & licenses",
        "courses & certifications",
        "accreditations",
        "awards & certifications",
        "achievements",
        "hackathons",
        "achievements & hackathons",
        "awards & achievements",
        "honors & awards",
        "honors",
        "awards",
    ],
}

# Inverted mapping: normalized keyword -> canonical section
KEYWORD_TO_SECTION: dict[str, str] = {}
for canonical, keywords in SECTION_TAXONOMY.items():
    for kw in keywords:
        KEYWORD_TO_SECTION[kw] = canonical

# Bullet characters that indicate body list items, NOT section titles
BULLET_CHARS = ("•", "-", "*", "▪", "▫", "–", "—", ">", "+", "►")


# ---------------------------------------------------------------------------
# 2. Contact Information Regex Patterns
# ---------------------------------------------------------------------------

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b", re.IGNORECASE
)

PHONE_PATTERN = re.compile(
    r"(?:\+?91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b|"
    r"(?:\+?1[\-\s]?)?\(?[2-9]\d{2}\)?[\-\s]?[2-9]\d{2}[\-\s]?\d{4}\b|"
    r"(?:\+?\d{1,3}[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}\b"
)

LINKEDIN_PATTERN = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)

GITHUB_PATTERN = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)

WEBSITE_PATTERN = re.compile(
    r"\b(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.(?:dev|me|tech|site|online|io|app|com|in|org))(?:\/[^\s,]*)?\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# 3. Helper Functions: Line Analysis & Section Scoring
# ---------------------------------------------------------------------------

def clean_cid_artifacts(text: str) -> str:
    """Removes PDF font glyph encoding artifacts like (cid:131)."""
    return re.sub(r"\(cid:\d+\)", " ", text).strip()


def despace_letters(text: str) -> str:
    """
    Handles PDF kerning where letters are spaced out, e.g.:
    'E D U C A T I O N' -> 'EDUCATION'
    'T E C H N I C A L   S K I L L S' -> 'TECHNICAL SKILLS'
    """
    cleaned = text.strip()
    # If text is heavily spaced single uppercase letters
    if re.search(r"\b[A-Z]\s+[A-Z]\s+[A-Z]\b", cleaned):
        words = re.split(r"\s{2,}", cleaned)
        despaced_words = [
            re.sub(r"(?<=\b[A-Za-z0-9])\s(?=[A-Za-z0-9]\b)", "", w) for w in words
        ]
        return " ".join(despaced_words)
    return cleaned


def normalize_heading(text: str) -> str:
    """Strip common punctuation, formatting artifacts, and normalize spaces."""
    cleaned = clean_cid_artifacts(text)
    cleaned = despace_letters(cleaned)
    cleaned = cleaned.strip()
    # Strip leading/trailing non-alphanumeric (bullets, colons, dashes)
    cleaned = re.sub(r"^[\s•\-*▪▫–—>+#:|§]+", "", cleaned)
    cleaned = re.sub(r"[\s:|#\-_§]+$", "", cleaned)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.lower()


def is_bullet_or_sentence(line: str) -> bool:
    """Check if line is a bullet item or a full narrative sentence rather than a heading."""
    stripped = clean_cid_artifacts(line).strip()
    if not stripped:
        return False
    # Starts with a bullet character
    if any(stripped.startswith(b) for b in BULLET_CHARS):
        return True
    # Starts with numbered list (e.g., '1.', '1)')
    if re.match(r"^\d+[\.\)]\s+", stripped):
        return True
    # Word count check: section headers rarely exceed 5 words
    words = stripped.split()
    if len(words) > 5:
        return True
    # Length check: headers rarely exceed 45 characters
    if len(stripped) > 45:
        return True
    # Ends with full stop or sentence punctuation
    if stripped.endswith((".", "!", ",", ";")):
        return True
    return False


def classify_section_header(
    line: str,
    font_size: Optional[float] = None,
    is_bold: bool = False,
    median_font_size: Optional[float] = None,
) -> Tuple[Optional[str], float]:
    """
    Evaluates whether a candidate line is a section header using hybrid scoring.
    Returns: (canonical_section_name or None, confidence_score 0..100)
    """
    stripped = line.strip()
    if not stripped or is_bullet_or_sentence(stripped):
        return None, 0.0

    normalized = normalize_heading(stripped)
    if not normalized:
        return None, 0.0

    # 1. Exact ontology keyword match
    canonical = KEYWORD_TO_SECTION.get(normalized)
    score = 0.0

    if canonical:
        score += 65.0
    elif "examination" in normalized and any(
        k in normalized for k in ("university", "institute", "degree", "cpi", "gpa", "board", "year")
    ):
        canonical = "education"
        score += 70.0
    else:
        # Check partial prefix/suffix match (e.g., "technical skills & proficiencies")
        for kw, sec in KEYWORD_TO_SECTION.items():
            if (
                normalized == kw
                or normalized.startswith(f"{kw} ")
                or normalized.endswith(f" {kw}")
                or f" & {kw}" in normalized
                or f" and {kw}" in normalized
            ):
                canonical = sec
                score += 50.0
                break

    if not canonical:
        return None, 0.0

    # 2. Typography features (if PDF layout metadata available)
    if font_size and median_font_size and median_font_size > 0:
        if font_size >= median_font_size * 1.15:
            score += 25.0
        elif font_size >= median_font_size * 1.05:
            score += 15.0

    if is_bold:
        score += 15.0

    # 3. Capitalization features
    despaced = despace_letters(stripped)
    if despaced.isupper() and len(despaced) > 2:
        score += 15.0
    elif despaced.istitle():
        score += 8.0

    # Threshold for positive classification
    if score >= 55.0:
        return canonical, min(score, 100.0)

    return None, 0.0


# ---------------------------------------------------------------------------
# 4. Identity & Contact Information Extraction
# ---------------------------------------------------------------------------

def extract_contact_info(text: str, hyperlinks: Optional[list[str]] = None) -> dict[str, str]:
    """
    Deterministically extracts email, phone, LinkedIn, GitHub, and portfolio links.
    Also inspects PDF embedded hyperlinks for links behind anchor text.
    """
    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    linkedin = LINKEDIN_PATTERN.findall(text)
    github = GITHUB_PATTERN.findall(text)

    contact = {
        "email": emails[0] if emails else "",
        "phone": "",
        "linkedin": f"https://linkedin.com/in/{linkedin[0]}" if linkedin else "",
        "github": f"https://github.com/{github[0]}" if github else "",
        "portfolio": "",
    }

    # Clean phone numbers
    for p in phones:
        digits = re.sub(r"\D", "", p)
        if len(digits) >= 10:
            contact["phone"] = p.strip()
            break

    # Extract from embedded hyperlinks if not found in plain text
    if hyperlinks:
        for url in hyperlinks:
            if not url:
                continue
            lower_url = url.lower()
            if not contact["email"] and lower_url.startswith("mailto:"):
                contact["email"] = url.replace("mailto:", "").split("?")[0].strip()
            elif not contact["phone"] and lower_url.startswith("tel:"):
                contact["phone"] = url.replace("tel:", "").strip()
            elif not contact["linkedin"] and "linkedin.com/in/" in lower_url:
                contact["linkedin"] = url.strip()
            elif not contact["github"] and "github.com/" in lower_url and "github.io" not in lower_url:
                # Avoid picking up project URLs as main github
                if re.match(r"^https?:\/\/(?:www\.)?github\.com\/[^\/]+\/?$", url):
                    contact["github"] = url.strip()
                elif not contact["github"]:
                    contact["github"] = url.strip()
            elif not contact["portfolio"] and ("github.io" in lower_url or "portfolio" in lower_url or "vercel.app" in lower_url):
                contact["portfolio"] = url.strip()

    # Extract personal website/portfolio from text if still empty
    if not contact["portfolio"]:
        common_mail_domains = {
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
            "proton.me", "protonmail.com", "mail.com", "aol.com", "live.com",
            "zoho.com", "yandex.com", "gmx.com", "dau.ac.in",
        }
        tech_keywords = {
            "socket.io", "vue.js", "node.js", "next.js", "react.js", "three.js",
            "express.js", "chart.js", "nest.js", "nuxt.js", "electron.js"
        }
        for match in WEBSITE_PATTERN.finditer(text):
            found_url = match.group(0).strip()
            lower_u = found_url.lower()
            if (
                "linkedin" not in lower_u
                and "github" not in lower_u
                and "@" not in lower_u
                and lower_u not in common_mail_domains
                and lower_u not in tech_keywords
                and not lower_u.endswith((".pdf", ".png", ".jpg", ".jpeg"))
            ):
                contact["portfolio"] = found_url
                break

    return contact


def extract_candidate_name(header_lines: list[str]) -> str:
    """
    Extracts candidate name from the top header lines before the first section.
    Filters out emails, phones, URLs, and labels.
    """
    for line in header_lines:
        clean = clean_cid_artifacts(line).strip()
        clean = despace_letters(clean)
        if not clean:
            continue
        # Skip lines with contact patterns
        if "@" in clean or "http" in clean.lower() or "www." in clean.lower():
            continue
        if re.search(r"\d{3,}", clean):  # skip phones or street numbers
            continue
        # Candidate names are typically 1 to 4 words
        words = clean.split()
        if 1 <= len(words) <= 4:
            # Check for letters only (plus periods for initials)
            if all(re.match(r"^[A-Za-z\.\'-]+$", w) for w in words):
                return clean
    return ""


def detect_column_split(page: Any) -> Optional[float]:
    """
    Detects if a PDF page has a two-column layout by finding a vertical gutter
    between 30% and 75% width where few or no words cross, and both sides have content.
    Returns the x-coordinate split point, or None if single column.
    """
    try:
        words = page.extract_words()
        if not words or len(words) < 40:
            return None

        width = float(page.width)
        min_x = width * 0.30
        max_x = width * 0.75

        best_split = None
        min_crossings = 9999
        step = 5.0
        curr_x = min_x

        while curr_x <= max_x:
            left_words = [w for w in words if w["x1"] <= curr_x]
            right_words = [w for w in words if w["x0"] >= curr_x]
            crossing_words = [w for w in words if w["x0"] < curr_x < w["x1"]]

            if len(left_words) >= 20 and len(right_words) >= 20:
                if len(crossing_words) < min_crossings:
                    min_crossings = len(crossing_words)
                    best_split = curr_x
            curr_x += step

        if best_split is not None and min_crossings <= 1:
            return best_split
    except Exception as exc:
        logger.debug(f"detect_column_split exception: {exc}")
    return None


# ---------------------------------------------------------------------------
# 5. Core Parser: Layout-Aware PDF Parser (Strategy D)
# ---------------------------------------------------------------------------

def parse_resume_from_pdf(pdf_bytes: bytes) -> dict[str, Any]:
    """
    Fast, deterministic resume section parser using PDF layout geometry,
    extract_text_lines, font metadata, and embedded hyperlinks.
    Does NOT invoke any LLM. Execution time: ~10-30ms.
    """
    sections: dict[str, list[str]] = {
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
    }
    header_lines: list[str] = []
    full_text_lines: list[str] = []
    extracted_hyperlinks: list[str] = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # 1. Collect hyperlinks from all pages
            for page in pdf.pages:
                if hasattr(page, "hyperlinks") and page.hyperlinks:
                    for h in page.hyperlinks:
                        uri = h.get("uri")
                        if uri:
                            extracted_hyperlinks.append(uri)

            # 2. Extract lines using extract_text_lines (with multi-column auto-detection)
            all_line_sizes: list[float] = []
            extracted_pages_lines: list[list[dict[str, Any]]] = []

            for page in pdf.pages:
                split_x = detect_column_split(page)
                if split_x:
                    col1 = page.crop((0, 0, split_x, float(page.height)))
                    col2 = page.crop((split_x, 0, float(page.width), float(page.height)))
                    text_lines = (col1.extract_text_lines(layout=False) or []) + (
                        col2.extract_text_lines(layout=False) or []
                    )
                else:
                    text_lines = page.extract_text_lines(layout=False) or []
                page_data: list[dict[str, Any]] = []

                for l in text_lines:
                    line_text = l.get("text", "").strip()
                    if not line_text:
                        continue

                    chars = l.get("chars", [])
                    sizes = [float(c.get("size", 10.0)) for c in chars if c.get("size")]
                    avg_size = statistics.mean(sizes) if sizes else 10.0
                    all_line_sizes.append(avg_size)

                    is_bold = any(
                        "bold" in str(c.get("fontname", "")).lower()
                        or "black" in str(c.get("fontname", "")).lower()
                        or "cmbx" in str(c.get("fontname", "")).lower()  # LaTeX bold
                        or "heavy" in str(c.get("fontname", "")).lower()
                        for c in chars
                    )

                    page_data.append({
                        "text": line_text,
                        "font_size": avg_size,
                        "is_bold": is_bold,
                    })

                extracted_pages_lines.append(page_data)

            # Compute median line font size
            median_font_size = (
                statistics.median(all_line_sizes) if all_line_sizes else 10.0
            )

            # 3. Finite State Machine for Boundary Segmentation
            current_section: Optional[str] = None

            for page_data in extracted_pages_lines:
                for line_item in page_data:
                    text = line_item["text"]
                    font_size = line_item["font_size"]
                    is_bold = line_item["is_bold"]

                    full_text_lines.append(text)

                    # Classify if this line is a section header
                    section_name, confidence = classify_section_header(
                        line=text,
                        font_size=font_size,
                        is_bold=is_bold,
                        median_font_size=median_font_size,
                    )

                    if section_name:
                        current_section = section_name
                    elif current_section is not None:
                        sections[current_section].append(text)
                    else:
                        header_lines.append(text)

    except Exception as exc:
        logger.warning(f"extract_text_lines parsing failed, falling back to text stream: {exc}")
        return parse_resume_from_text(pdf_bytes.decode("utf-8", errors="ignore"))

    combined_full_text = "\n".join(full_text_lines)
    candidate_name = extract_candidate_name(header_lines)
    contact_info = extract_contact_info(combined_full_text, hyperlinks=extracted_hyperlinks)
    tech_data = extract_tech_keywords(combined_full_text)

    found_sections = [k for k, v in sections.items() if v]
    skills_list = tech_data.get("extracted_skills", [])
    logger.info(
        f"Parsed PDF resume: candidate='{candidate_name}', sections={found_sections}, "
        f"skills_count={len(skills_list)}, text_length={len(combined_full_text)} chars"
    )

    return {
        "candidate_name": candidate_name,
        "summary": "\n".join(sections["summary"]).strip(),
        "experience": "\n".join(sections["experience"]).strip(),
        "education": "\n".join(sections["education"]).strip(),
        "skills": "\n".join(sections["skills"]).strip(),
        "projects": "\n".join(sections["projects"]).strip(),
        "certifications": "\n".join(sections["certifications"]).strip(),
        "contact_info": contact_info,
        "tech_skills": skills_list,
        "skills_by_domain": tech_data.get("skills_by_domain", {}),
        "top_recommended_roles": tech_data.get("top_recommended_roles", []),
        # "role_affinities": tech_data.get("role_affinities", {}),
        "parser_type": "deterministic_layout_hybrid",
    }


# ---------------------------------------------------------------------------
# 6. Core Parser: Pure Plain Text Parser (Fallback)
# ---------------------------------------------------------------------------

def parse_resume_from_text(raw_text: str) -> dict[str, Any]:
    """
    Deterministic resume section parser from raw text string.
    Useful for plain text inputs, clipboard text, or DOCX streams.
    Execution time: ~2-5ms.
    """
    sections: dict[str, list[str]] = {
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
    }
    header_lines: list[str] = []
    current_section: Optional[str] = None

    lines = raw_text.splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        section_name, confidence = classify_section_header(
            line=stripped,
            font_size=None,
            is_bold=False,
            median_font_size=None,
        )

        if section_name:
            current_section = section_name
        elif current_section is not None:
            sections[current_section].append(stripped)
        else:
            header_lines.append(stripped)

    candidate_name = extract_candidate_name(header_lines)
    contact_info = extract_contact_info(raw_text)
    tech_data = extract_tech_keywords(raw_text)

    found_sections = [k for k, v in sections.items() if v]
    skills_list = tech_data.get("extracted_skills", [])
    logger.info(
        f"Parsed text resume: candidate='{candidate_name}', sections={found_sections}, "
        f"skills_count={len(skills_list)}, text_length={len(raw_text)} chars"
    )

    return {
        "candidate_name": candidate_name,
        "summary": "\n".join(sections["summary"]).strip(),
        "experience": "\n".join(sections["experience"]).strip(),
        "education": "\n".join(sections["education"]).strip(),
        "skills": "\n".join(sections["skills"]).strip(),
        "projects": "\n".join(sections["projects"]).strip(),
        "certifications": "\n".join(sections["certifications"]).strip(),
        "contact_info": contact_info,
        "tech_skills": skills_list,
        "skills_by_domain": tech_data.get("skills_by_domain", {}),
        "top_recommended_roles": tech_data.get("top_recommended_roles", []),
        # "role_affinities": tech_data.get("role_affinities", {}),
        "parser_type": "deterministic_text",
    }
