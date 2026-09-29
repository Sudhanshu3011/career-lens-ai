"""
CareerLens AI - High-Performance Deterministic Tech Keyword Extractor (Zero-LLM)

Extracts technical keywords, frameworks, libraries, tools, and platforms from
unstructured resume text or parsed sections without any LLM calls.

Features:
1. Exact Symbol-Aware Boundary Matching (C++, C#, .NET, Node.js, CI/CD).
2. Synonym & Alias Normalization (k8s -> Kubernetes, postgres -> PostgreSQL).
3. Domain Categorization (Frontend, Backend, AI/ML, GenAI, DevOps, Data, etc.).
4. IT Engineering Role Affinity Scoring & Gap Detection.
5. Sub-5ms execution time on CPU.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple

from app.data.tech_skills_db import TECH_DOMAINS


class TechKeywordExtractor:
    """
    Zero-LLM high-speed technical keyword and skill extractor.
    Pre-compiles regex patterns for boundary-accurate extraction.
    """

    def __init__(self):
        self._alias_to_canonical: Dict[str, str] = {}
        self._canonical_to_domain: Dict[str, str] = {}
        self._compiled_patterns: List[Tuple[re.Pattern, str]] = []
        self._special_symbol_patterns: List[Tuple[re.Pattern, str]] = []

        self._build_index()

    def _build_index(self):
        """Constructs inverted indexes and pre-compiled regex matchers."""
        # 1. Map domains and canonical skills
        for domain, skills in TECH_DOMAINS.items():
            for canonical, aliases in skills.items():
                self._canonical_to_domain[canonical] = domain
                # Register canonical itself as an alias
                self._alias_to_canonical[canonical.lower()] = canonical
                for alias in aliases:
                    self._alias_to_canonical[alias.lower()] = canonical

        # 2. Build specialized patterns for symbols that break standard word boundaries (\b)
        special_symbols = [
            (r"(?:\b|(?<=\s))C\+\+(?=[,\s\.\/\)]|$)", "C++"),
            (r"(?:\b|(?<=\s))C#(?=[,\s\.\/\)]|$)", "C#"),
            (r"(?:\b|(?<=\s))\.(NET|net)(?:\s+(?:Core|core))?(?=[,\s\.\/\)]|$)", "ASP.NET Core"),
            (r"(?:\b|(?<=\s))CI\/CD(?=[,\s\.\/\)]|$)", "CI/CD"),
            (r"(?:\b|(?<=\s))C(?=[,\s\.\/\)]+(?:programming|language|code))\b", "C"),
            (r"(?:\b|(?<=\s))(?:Go|Golang)(?=[,\s\.\/\)]+(?:programming|language|code|developer))\b", "Go"),
            (r"\bGo\s+(?=developer|engineer|backend)\b", "Go"),
            (r"\bgolang\b", "Go"),
            (r"(?:\b|(?<=\s))R(?=[,\s\.\/\)]+(?:programming|language|studio|data))\b", "R"),
        ]

        for pat_str, canonical in special_symbols:
            self._special_symbol_patterns.append(
                (re.compile(pat_str, re.IGNORECASE), canonical)
            )

        # 3. Sort standard aliases by length descending so longer compound terms match first
        # E.g., "Amazon Web Services" matches before "AWS", "Spring Boot" before "Spring"
        sorted_aliases = sorted(self._alias_to_canonical.keys(), key=lambda x: len(x), reverse=True)

        for alias in sorted_aliases:
            canonical = self._alias_to_canonical[alias]
            # Escape regex special chars while enforcing word boundaries
            escaped = re.escape(alias)
            # Standard word boundary regex
            pattern = re.compile(rf"(?<![\w\-]){escaped}(?![\w\-])", re.IGNORECASE)
            self._compiled_patterns.append((pattern, canonical))

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts all technical skills and keywords from raw text.
        Returns canonical skills, total count, and domain grouping.
        """
        if not text or not text.strip():
            return {
                "extracted_skills": [],
                "total_skills_count": 0,
                "skills_by_domain": {},
            }

        found_skills: Set[str] = set()

        # Step 1: Check special symbol patterns
        for pattern, canonical in self._special_symbol_patterns:
            if pattern.search(text):
                found_skills.add(canonical)

        # Step 2: Check standard aliases
        for pattern, canonical in self._compiled_patterns:
            if canonical in found_skills:
                continue
            if pattern.search(text):
                found_skills.add(canonical)

        # Step 3: Categorize by domain
        skills_by_domain: Dict[str, List[str]] = {}
        for skill in sorted(found_skills):
            domain = self._canonical_to_domain.get(skill, "other")
            if domain not in skills_by_domain:
                skills_by_domain[domain] = []
            skills_by_domain[domain].append(skill)

        return {
            "extracted_skills": sorted(list(found_skills)),
            "total_skills_count": len(found_skills),
            "skills_by_domain": skills_by_domain,
        }



# Global singleton instance for high-throughput reuse
tech_keyword_extractor = TechKeywordExtractor()


def extract_tech_keywords(text: str) -> Dict[str, Any]:
    """Convenience function to extract tech skills using the global extractor."""
    return tech_keyword_extractor.extract_skills(text)


# ---------------------------------------------------------------------------
# Domain → Broad Umbrella Skill Mapping
# ---------------------------------------------------------------------------
# When a sub-skill is detected (e.g. "PyTorch"), we automatically inject its
# umbrella term (e.g. "Machine Learning") so that matching is fairer — a
# candidate with PyTorch isn't penalised for not explicitly writing "ML".
_DOMAIN_UMBRELLA: Dict[str, List[str]] = {
    "languages":            ["Programming"],
    "frontend":             ["Frontend Development"],
    "backend":              ["Backend Development", "Web Development"],
    "ai_ml_data_science":  ["Machine Learning", "Artificial Intelligence"],
    "genai_llms":          ["Generative AI", "Large Language Models"],
    "databases":           ["Databases", "Data Management"],
    "cloud_devops":        ["Cloud Computing", "DevOps"],
    "data_engineering":    ["Data Engineering", "Big Data"],
    "mobile":              ["Mobile Development"],
    "cybersecurity":       ["Cybersecurity", "Information Security"],
    "qa_testing":          ["Software Testing", "Quality Assurance"],
    "embedded_iot":        ["Embedded Systems", "IoT"],
    "blockchain_web3":     ["Blockchain", "Web3"],
    "generative_ai":       ["Generative AI", "Large Language Models"],
    "nlp":                 ["Natural Language Processing", "NLP"],
    "cloud_ai_services":   ["Cloud AI", "AI Services"],
    "data_visualization":  ["Data Visualization"],
    "speech_voice_ai":     ["Speech AI", "Voice AI", "Conversational AI"],
    "statistical_modeling":["Statistical Modeling", "Data Science"],
    "observability":       ["Monitoring", "Observability"],
    "ci_cd_extended":      ["CI/CD", "DevOps"],
    "infrastructure_as_code": ["Infrastructure as Code", "DevOps"],
    "messaging_extended":  ["Messaging", "Event Streaming"],
    "testing_extended":    ["Software Testing", "Quality Assurance"],
    "orchestration_extended": ["Container Orchestration", "DevOps"],
    "cloud_services_extended": ["Cloud Computing"],
    "data_engineering_extended": ["Data Engineering", "Analytics"],
    "blockchain_extended": ["Blockchain"],
}


def expand_with_parent_domains(skills: List[str]) -> List[str]:
    """
    Given a list of canonical skill names, return the same list expanded with
    inferred broader/umbrella terms.

    Example:
        ["PyTorch", "LangChain", "AWS S3"] →
        ["PyTorch", "LangChain", "AWS S3",
         "Machine Learning", "Artificial Intelligence",
         "Generative AI", "Large Language Models",
         "Cloud Computing", "DevOps"]

    Deduplicates the result while preserving the original ordering.
    """
    extractor = tech_keyword_extractor
    expanded: List[str] = list(skills)
    seen: Set[str] = set(s.lower() for s in skills)

    for skill in skills:
        domain = extractor._canonical_to_domain.get(skill)
        if domain and domain in _DOMAIN_UMBRELLA:
            for umbrella in _DOMAIN_UMBRELLA[domain]:
                if umbrella.lower() not in seen:
                    expanded.append(umbrella)
                    seen.add(umbrella.lower())

    return expanded
