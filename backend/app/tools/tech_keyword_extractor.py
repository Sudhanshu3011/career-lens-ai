"""
CareerLens AI - Tech Keyword Extractor (Backward-Compatibility Shim)

Re-exports skill extraction classes and functions from app.parsers.skill_extractor.
"""

from __future__ import annotations

from app.parsers.skill_extractor import (
    TechnicalSkillExtractor as TechKeywordExtractor,
    extract_tech_keywords,
    skill_extractor,
)

__all__ = [
    "TechKeywordExtractor",
    "extract_tech_keywords",
    "skill_extractor",
]
