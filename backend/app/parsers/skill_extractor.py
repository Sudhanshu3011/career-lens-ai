"""
CareerLens AI - Technical Skill & Competency Extractor (Zero-LLM)

Extracts technical keywords, frameworks, libraries, tools, and platforms from
unstructured resume text or parsed sections without any LLM calls (<5ms execution).

Features:
1. Exact Symbol-Aware Boundary Matching (C++, C#, .NET, Node.js, CI/CD).
2. Synonym & Alias Normalization (k8s -> Kubernetes, postgres -> PostgreSQL).
3. 14 IT Domain Categorization.
4. Role Affinity Scoring across 17 IT engineering profiles.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple

from app.data.tech_skills_db import TECH_DOMAINS, calculate_role_affinity


class TechnicalSkillExtractor:
    """
    Zero-LLM high-speed technical skill extractor.
    Pre-compiles regex patterns for boundary-accurate extraction and domain clustering.
    """

    def __init__(self) -> None:
        self._alias_to_canonical: Dict[str, str] = {}
        self._canonical_to_domain: Dict[str, str] = {}
        self._compiled_patterns: List[Tuple[re.Pattern, str]] = []
        self._special_symbol_patterns: List[Tuple[re.Pattern, str]] = []

        self._build_index()

    def _build_index(self) -> None:
        """Constructs inverted indexes and pre-compiled regex matchers."""
        for domain, skills in TECH_DOMAINS.items():
            for canonical, aliases in skills.items():
                self._canonical_to_domain[canonical] = domain
                self._alias_to_canonical[canonical.lower()] = canonical
                for alias in aliases:
                    self._alias_to_canonical[alias.lower()] = canonical

        special_symbols = [
            (r"(?:\b|(?<=\s))C\+\+(?=[,\s\.\/\)]|$)", "C++"),
            (r"(?:\b|(?<=\s))C#(?=[,\s\.\/\)]|$)", "C#"),
            (
                r"(?:\b|(?<=\s))\.(NET|net)(?:\s+(?:Core|core))?(?=[,\s\.\/\)]|$)",
                "ASP.NET Core",
            ),
            (r"(?:\b|(?<=\s))CI\/CD(?=[,\s\.\/\)]|$)", "CI/CD"),
            (r"(?:\b|(?<=\s))C(?=[,\s\.\/\)]+(?:programming|language|code))\b", "C"),
            (
                r"(?:\b|(?<=\s))(?:Go|Golang)(?=[,\s\.\/\)]+(?:programming|language|code|developer))\b",
                "Go",
            ),
            (r"\bGo\s+(?=developer|engineer|backend)\b", "Go"),
            (r"\bgolang\b", "Go"),
            (
                r"(?:\b|(?<=\s))R(?=[,\s\.\/\)]+(?:programming|language|studio|data))\b",
                "R",
            ),
        ]

        for pat_str, canonical in special_symbols:
            self._special_symbol_patterns.append(
                (re.compile(pat_str, re.IGNORECASE), canonical)
            )

        sorted_aliases = sorted(
            self._alias_to_canonical.keys(), key=lambda x: len(x), reverse=True
        )

        for alias in sorted_aliases:
            canonical = self._alias_to_canonical[alias]
            escaped = re.escape(alias)
            pattern = re.compile(rf"(?<![\w\-]){escaped}(?![\w\-])", re.IGNORECASE)
            self._compiled_patterns.append((pattern, canonical))

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts all technical skills from raw text and calculates role affinities.
        """
        if not text or not text.strip():
            return {
                "extracted_skills": [],
                "total_skills_count": 0,
                "skills_by_domain": {},
                "role_affinities": {},
                "top_recommended_roles": [],
            }

        found_skills: Set[str] = set()

        # Step 1: Special symbol patterns
        for pattern, canonical in self._special_symbol_patterns:
            if pattern.search(text):
                found_skills.add(canonical)

        # Step 2: Standard aliases
        for pattern, canonical in self._compiled_patterns:
            if canonical in found_skills:
                continue
            if pattern.search(text):
                found_skills.add(canonical)

        # Step 3: Domain categorization
        skills_by_domain: Dict[str, List[str]] = {}
        for skill in sorted(found_skills):
            domain = self._canonical_to_domain.get(skill, "other")
            if domain not in skills_by_domain:
                skills_by_domain[domain] = []
            skills_by_domain[domain].append(skill)

        # Step 4: Role affinities
        sorted_skills = sorted(list(found_skills))
        role_affinities = calculate_role_affinity(sorted_skills)
        top_recommended_roles = [r["role"] for r in role_affinities[:3]]

        return {
            "extracted_skills": sorted_skills,
            "total_skills_count": len(found_skills),
            "skills_by_domain": skills_by_domain,
            "role_affinities": role_affinities,
            "top_recommended_roles": top_recommended_roles,
        }


# Singleton instance
skill_extractor = TechnicalSkillExtractor()


def extract_tech_keywords(text: str) -> Dict[str, Any]:
    """Convenience functional interface for technical skill extraction."""
    return skill_extractor.extract_skills(text)
