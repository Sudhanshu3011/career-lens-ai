"""
CareerLens AI - Blueprint to System One Adapter
Compiles the recruiter-friendly EvaluationQuestionsBlueprint and customized questions
into TypeSafe SDK primitives (Choice, Score, Noul) with mandatory gate configuration.
Compatible with both TypeSafe Jev (Cloud) and ConvAI Laya (Local).
"""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple
from typesafe_sdk import Choice, Noul, Score

from app.models.domain.dynamic_blueprint import EvaluationQuestionsBlueprint
from app.schemas.recruitment import EvaluationQuestionItem


def _slugify(text: str) -> str:
    """Converts a label into a clean alphanumeric snake_case identifier."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return clean[:30]


class BlueprintToEngineAdapter:
    """Translates high-level recruiter blueprints into TypeSafe System One question sets."""

    @staticmethod
    def compile_questions(
        blueprint: EvaluationQuestionsBlueprint,
    ) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Compiles the blueprint into:
        1. questions: Dict[str, Union[Choice, Score, Noul]] consumed by Jev / Laya.
        2. gate_registry: Dict[str, Dict[str, Any]] mapping gate_key -> {'name': ..., 'question': ..., 'is_mandatory': True}.
        """
        questions: Dict[str, Any] = {
            # 1. Domain Alignment (Choice)
            "domain_alignment": Choice(
                instructions=blueprint.domain_alignment.question,
                criteria=blueprint.domain_alignment.options,
            ),
            # 2. Seniority Assessment (Score 0-5)
            "seniority_level": Score(
                instructions=blueprint.seniority_assessment.question,
                criteria=blueprint.seniority_assessment.levels,
            ),
            # 3. Competency Depth (Score 0-5)
            "competency_depth": Score(
                instructions=blueprint.competency_depth_assessment.question,
                criteria=blueprint.competency_depth_assessment.levels,
            ),
            # 4. Evidence Quality (Score 0-5)
            "evidence_quality": Score(
                instructions=blueprint.evidence_quality_assessment.question,
                criteria=blueprint.evidence_quality_assessment.levels,
            ),
        }

        # 5. Experience Duration Fit (Score 0-5)
        if blueprint.experience_duration_assessment:
            questions["experience_duration"] = Score(
                instructions=blueprint.experience_duration_assessment.question,
                criteria=blueprint.experience_duration_assessment.levels,
            )

        # 6. Education Credentials Relevance (Score 0-5)
        if blueprint.education_credentials_assessment:
            questions["education_credentials"] = Score(
                instructions=blueprint.education_credentials_assessment.question,
                criteria=blueprint.education_credentials_assessment.levels,
            )

        gate_registry: Dict[str, Dict[str, Any]] = {}

        # 7. Mandatory Dealbreaker Gates (Noul)
        for idx, gate in enumerate(blueprint.mandatory_dealbreakers):
            gate_key = gate.name.strip()
            if not gate_key:
                gate_key = f"Dealbreaker Requirement {idx + 1}"
            elif gate_key in questions:
                gate_key = f"{gate_key} ({idx + 1})"

            questions[gate_key] = Noul(instructions=gate.question)
            gate_registry[gate_key] = {
                "name": gate.name,
                "question": gate.question,
                "is_mandatory": True,
            }

        return questions, gate_registry

    @staticmethod
    def blueprint_to_question_items(
        blueprint: EvaluationQuestionsBlueprint,
    ) -> Dict[str, EvaluationQuestionItem]:
        """Converts an EvaluationQuestionsBlueprint into a dictionary of editable EvaluationQuestionItem models."""
        items: Dict[str, EvaluationQuestionItem] = {
            "domain_alignment": EvaluationQuestionItem(
                name="domain_alignment",
                type="choice",
                primitive="Choice",
                scale="Categorical Classification: direct_domain_match, adjacent_domain_transfer, unrelated_background",
                instructions=blueprint.domain_alignment.question,
                is_mandatory=False,
                category="domain",
            ),
            "seniority_level": EvaluationQuestionItem(
                name="seniority_level",
                type="score",
                primitive="Score",
                scale="Ascending Scale: Level 0 (Intern) to Level 5 (Senior/Principal Leader)",
                instructions=blueprint.seniority_assessment.question,
                is_mandatory=False,
                category="seniority",
            ),
            "competency_depth": EvaluationQuestionItem(
                name="competency_depth",
                type="score",
                primitive="Score",
                scale="Ascending Scale: Level 0 (None) to Level 5 (Mastery/Super-user)",
                instructions=blueprint.competency_depth_assessment.question,
                is_mandatory=False,
                category="depth",
            ),
            "evidence_quality": EvaluationQuestionItem(
                name="evidence_quality",
                type="score",
                primitive="Score",
                scale="Ascending Scale: Level 0 (Unsubstantiated) to Level 5 (Exceptional Impact)",
                instructions=blueprint.evidence_quality_assessment.question,
                is_mandatory=False,
                category="evidence",
            ),
        }

        if blueprint.experience_duration_assessment:
            items["experience_duration"] = EvaluationQuestionItem(
                name="experience_duration",
                type="score",
                primitive="Score",
                scale="Ascending Scale: Level 0 (None/Intern) to Level 5 (Industry Veteran / Exceeds Required Years)",
                instructions=blueprint.experience_duration_assessment.question,
                is_mandatory=False,
                category="experience",
            )

        if blueprint.education_credentials_assessment:
            items["education_credentials"] = EvaluationQuestionItem(
                name="education_credentials",
                type="score",
                primitive="Score",
                scale="Ascending Scale: Level 0 (None/Unrelated) to Level 5 (Doctorate/Terminal or Exact Accredited Degree)",
                instructions=blueprint.education_credentials_assessment.question,
                is_mandatory=False,
                category="education",
            )

        for idx, gate in enumerate(blueprint.mandatory_dealbreakers):
            gate_key = gate.name.strip() or f"Dealbreaker Requirement {idx + 1}"
            items[gate_key] = EvaluationQuestionItem(
                name=gate_key,
                type="noul",
                primitive="Noul",
                scale="Binary Truth Judgment P(True) in [0.0, 1.0]",
                instructions=gate.question,
                is_mandatory=True,
                category="gate",
            )

        return items

    @staticmethod
    def compile_from_configured_questions(
        configured_questions: Dict[str, Any],
        blueprint: EvaluationQuestionsBlueprint,
    ) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Compiles recruiter-configured questions (with edited prompts or toggled is_mandatory flags)
        into executable TypeSafe questions and gate_registry.
        """
        questions: Dict[str, Any] = {}
        gate_registry: Dict[str, Dict[str, Any]] = {}

        # Default rubric criteria references from blueprint
        default_choice_crit = blueprint.domain_alignment.options
        default_seniority_crit = blueprint.seniority_assessment.levels
        default_competency_crit = blueprint.competency_depth_assessment.levels
        default_evidence_crit = blueprint.evidence_quality_assessment.levels
        default_experience_crit = (
            blueprint.experience_duration_assessment.levels
            if blueprint.experience_duration_assessment
            else default_seniority_crit
        )
        default_education_crit = (
            blueprint.education_credentials_assessment.levels
            if blueprint.education_credentials_assessment
            else default_competency_crit
        )

        for key, raw_item in configured_questions.items():
            if isinstance(raw_item, dict):
                item = EvaluationQuestionItem(**raw_item)
            elif isinstance(raw_item, EvaluationQuestionItem):
                item = raw_item
            else:
                continue

            q_type = item.type.lower()
            if q_type == "choice":
                questions[key] = Choice(
                    instructions=item.instructions,
                    criteria=default_choice_crit,
                )
            elif q_type == "score":
                crit = default_seniority_crit
                if "competency" in key.lower():
                    crit = default_competency_crit
                elif "evidence" in key.lower():
                    crit = default_evidence_crit
                elif "experience" in key.lower():
                    crit = default_experience_crit
                elif "education" in key.lower():
                    crit = default_education_crit
                questions[key] = Score(
                    instructions=item.instructions,
                    criteria=crit,
                )
            elif q_type == "noul":
                questions[key] = Noul(instructions=item.instructions)
                gate_registry[key] = {
                    "name": item.name,
                    "question": item.instructions,
                    "is_mandatory": item.is_mandatory,
                }

        # Ensure base dimensions exist even if user omitted them in payload
        if "domain_alignment" not in questions:
            questions["domain_alignment"] = Choice(
                instructions=blueprint.domain_alignment.question,
                criteria=blueprint.domain_alignment.options,
            )
        if "seniority_level" not in questions:
            questions["seniority_level"] = Score(
                instructions=blueprint.seniority_assessment.question,
                criteria=blueprint.seniority_assessment.levels,
            )
        if "competency_depth" not in questions:
            questions["competency_depth"] = Score(
                instructions=blueprint.competency_depth_assessment.question,
                criteria=blueprint.competency_depth_assessment.levels,
            )
        if "evidence_quality" not in questions:
            questions["evidence_quality"] = Score(
                instructions=blueprint.evidence_quality_assessment.question,
                criteria=blueprint.evidence_quality_assessment.levels,
            )
        if "experience_duration" not in questions and blueprint.experience_duration_assessment:
            questions["experience_duration"] = Score(
                instructions=blueprint.experience_duration_assessment.question,
                criteria=blueprint.experience_duration_assessment.levels,
            )
        if "education_credentials" not in questions and blueprint.education_credentials_assessment:
            questions["education_credentials"] = Score(
                instructions=blueprint.education_credentials_assessment.question,
                criteria=blueprint.education_credentials_assessment.levels,
            )

        return questions, gate_registry

