"""
CareerLens AI - Universal TypeSafe System One Architecture Test Suite
Validates:
1. Universal 6-Section Resume Parsing Data Contracts.
2. Dynamic Question Factory & Recruiter Blueprint Synthesis.
3. BlueprintToEngineAdapter Compilation to Choice, Score, Noul Primitives.
4. Speculative Fan-Out Early Reject Invariants:
   - Gate 1: Core Domain Viability (< 20% competency or unrelated background -> Flat REJECT 0.0).
   - Gate 2: Mandatory Dealbreaker Veto (P < 0.40 -> Cap <= 35.0, REJECT).
   - Gate 3: Universal Weighted Multipliers Calculation.
5. Cross-Industry Validation (Healthcare/Nursing and Tech/AI Engineering).
6. Dual Engine (Jev & Laya) Fan-Out Compatibility.
"""

import pytest
from app.models.domain.resume_sections import (
    EducationItem,
    ResumeParsedSections,
    WorkExperienceItem,
)
from app.models.domain.dynamic_blueprint import (
    AscendingAssessmentBlueprint,
    BackgroundClassificationBlueprint,
    EvaluationQuestionsBlueprint,
    MandatoryDealbreakerBlueprint,
)
from app.engines.question_factory.adapter import BlueprintToEngineAdapter
from app.engines.question_factory.generator import question_factory
from app.engines.evaluation.speculative_fanout import (
    DEFAULT_MULTIPLIERS,
    SpeculativeFanoutEvaluator,
    speculative_evaluator,
)
from app.engines.jev.client import JevClient
from app.engines.laya.client import LayaClient
from typesafe_sdk import Choice, Noul, Score


# ---------------------------------------------------------------------------
# 1. Universal 6 Canonical Sections Tests
# ---------------------------------------------------------------------------

def test_resume_parsed_sections_creation_and_formatting():
    """Verifies that ResumeParsedSections formats dense state text across all sections."""
    sections = ResumeParsedSections(
        candidate_name="Sarah Connor, BSN, RN",
        email="sarah.connor@hospital.org",
        phone="+1-555-0199",
        location="Atlanta, GA",
        portfolio_links=["https://nursingregistry.state.gov/rn/987654"],
        professional_summary="Critical Care ICU Staff Nurse with 5 years experience in Level 1 Trauma ICU.",
        work_experience=[
            WorkExperienceItem(
                employer="Metro General Hospital",
                role_title="ICU Charge Nurse",
                start_date="2021",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Managed 12-bed surgical ICU unit coordinating ECMO and mechanical ventilation.",
                    "Titrated critical vasoactive infusions maintaining zero medication errors.",
                ],
                tools_and_methods=["Arterial Lines", "Ventilators", "Epic EHR", "CRRT"],
            )
        ],
        core_competencies=["Hemodynamic Monitoring", "Mechanical Ventilation", "Critical Drip Titration"],
        competencies_by_category={"Critical Care": ["Ventilators", "Hemodynamic Monitoring"]},
        education=[
            EducationItem(
                institution="Emory University",
                degree_name="Bachelor of Science in Nursing (BSN)",
                field_of_study="Nursing",
                graduation_year=2019,
            )
        ],
        certifications_and_licenses=["Active Georgia RN License", "BLS", "ACLS", "CCRN"],
    )

    formatted = sections.format_for_evaluation()
    assert "=== CANDIDATE PROFILE: Sarah Connor, BSN, RN ===" in formatted
    assert "ICU Charge Nurse at Metro General Hospital" in formatted
    assert "Arterial Lines, Ventilators" in formatted
    assert "Hemodynamic Monitoring" in formatted
    assert "Active Georgia RN License" in formatted
    assert "Emory University" in formatted


# ---------------------------------------------------------------------------
# 2. Dynamic Blueprint & Adapter Tests
# ---------------------------------------------------------------------------

def test_dynamic_blueprint_compilation_to_typesafe_primitives():
    """Verifies that BlueprintToEngineAdapter compiles recruiter criteria into Choice, Score, and Noul."""
    blueprint = EvaluationQuestionsBlueprint(
        role_title="Critical Care / ICU Registered Nurse (RN)",
        seniority_target="Senior Staff Nurse",
        domain_alignment=BackgroundClassificationBlueprint(
            question="Classify candidate clinical background:",
            options={
                "direct_domain_match": "Acute ICU nursing background.",
                "adjacent_domain_transfer": "Telemetry or ED nursing background.",
                "unrelated_background": "Non-clinical background.",
            },
        ),
        seniority_assessment=AscendingAssessmentBlueprint(
            question="Rate clinical nursing seniority:",
            levels=[
                "Level 0: Student or unlicensed.",
                "Level 1: Novice (0-1 yr).",
                "Level 2: Competent (1-3 yrs).",
                "Level 3: Experienced (3-6 yrs).",
                "Level 4: Senior / Charge (6-10 yrs).",
                "Level 5: Clinical Specialist (10+ yrs).",
            ],
        ),
        competency_depth_assessment=AscendingAssessmentBlueprint(
            question="Rate ICU clinical competency depth:",
            levels=[
                "Level 0: No ICU exposure.",
                "Level 1: Basic knowledge.",
                "Level 2: Outpatient only.",
                "Level 3: Routine ICU ventilator care.",
                "Level 4: Advanced ECMO / CRRT.",
                "Level 5: Unit educator & protocol lead.",
            ],
        ),
        evidence_quality_assessment=AscendingAssessmentBlueprint(
            question="Rate clinical evidence quality:",
            levels=[
                "Level 0: No details.",
                "Level 1: Generic duties.",
                "Level 2: Descriptive tasks.",
                "Level 3: Detailed patient acuity.",
                "Level 4: Magnet hospital metrics.",
                "Level 5: National clinical awards.",
            ],
        ),
        mandatory_dealbreakers=[
            MandatoryDealbreakerBlueprint(
                name="Active State RN License",
                question="Does candidate hold an active unencumbered RN license?",
            ),
            MandatoryDealbreakerBlueprint(
                name="ACLS Certification",
                question="Does candidate hold an active ACLS certification?",
            ),
        ],
    )

    questions, registry = BlueprintToEngineAdapter.compile_questions(blueprint)

    # Validate primitives
    assert "domain_alignment" in questions
    assert isinstance(questions["domain_alignment"], Choice)
    assert "direct_domain_match" in questions["domain_alignment"].criteria

    assert "seniority_level" in questions
    assert isinstance(questions["seniority_level"], Score)
    assert len(questions["seniority_level"].criteria) == 6

    assert "competency_depth" in questions
    assert isinstance(questions["competency_depth"], Score)

    assert "evidence_quality" in questions
    assert isinstance(questions["evidence_quality"], Score)

    # Validate Noul binary gates
    assert "Active State RN License" in questions
    assert isinstance(questions["Active State RN License"], Noul)
    assert questions["Active State RN License"].instructions == "Does candidate hold an active unencumbered RN license?"

    assert "ACLS Certification" in questions
    assert isinstance(questions["ACLS Certification"], Noul)

    assert len(registry) == 2
    assert registry["Active State RN License"]["name"] == "Active State RN License"


# ---------------------------------------------------------------------------
# 3. Speculative Fan-Out Early Reject & Veto Invariant Tests
# ---------------------------------------------------------------------------

def test_speculative_gate_1_unrelated_domain_early_reject():
    """Gate 1: An applicant with unrelated background (e.g. Accountant applying for ICU Nurse) is flat rejected."""
    candidate = ResumeParsedSections(
        candidate_name="Bob Ledger, CPA",
        professional_summary="Senior Tax Auditor with 8 years in corporate tax accounting.",
        work_experience=[
            WorkExperienceItem(
                employer="Big 4 Accounting",
                role_title="Senior Tax Manager",
                responsibilities_and_achievements=["Audited Fortune 500 corporate balance sheets."],
                tools_and_methods=["QuickBooks", "Excel", "GAAP"],
            )
        ],
        core_competencies=["Tax Audit", "GAAP", "QuickBooks"],
    )

    answers = {
        "domain_alignment": {"choice": "unrelated_background"},
        "competency_depth": {"score": 0.0},
        "seniority_level": {"score": 4.0},  # Senior accountant
        "evidence_quality": {"score": 4.0},  # Strong audit metrics
        "gate_0_active_state_rn_license": {"probability": 0.0},
    }
    registry = {"gate_0_active_state_rn_license": {"name": "Active RN License", "question": "Has RN?"}}

    verdict = speculative_evaluator.evaluate(
        candidate_sections=candidate,
        answers=answers,
        gate_registry=registry,
    )

    assert verdict.fit_score == 0.0
    assert verdict.overall_decision == "REJECT"
    assert verdict.veto_reason == "domain_competency_gate_failed"
    assert "minimum required domain competencies" in verdict.summary_feedback


def test_speculative_gate_1_low_competency_early_reject():
    """Gate 1: Competency depth < 20% (Level 0) results in immediate flat REJECT (Score 0.0)."""
    candidate = ResumeParsedSections(
        candidate_name="Entry Novice",
        professional_summary="Casual enthusiast.",
        core_competencies=["None"],
    )

    answers = {
        "domain_alignment": {"choice": "direct_domain_match"},
        "competency_depth": {"score": 0.5},  # 0.5 / 5.0 = 10% < 20%
        "seniority_level": {"score": 1.0},
        "evidence_quality": {"score": 1.0},
    }

    verdict = speculative_evaluator.evaluate(
        candidate_sections=candidate,
        answers=answers,
        gate_registry={},
    )

    assert verdict.fit_score == 0.0
    assert verdict.overall_decision == "REJECT"
    assert verdict.veto_reason == "domain_competency_gate_failed"


def test_speculative_gate_2_mandatory_dealbreaker_veto_and_cap():
    """Gate 2: Candidate with good skills but missing mandatory license is vetoed and capped <= 35%."""
    candidate = ResumeParsedSections(
        candidate_name="Nurse Without License",
        professional_summary="Experienced clinical assistant.",
        work_experience=[
            WorkExperienceItem(
                employer="Clinic",
                role_title="Assistant",
                responsibilities_and_achievements=["Assisted clinical triage."],
            )
        ],
        core_competencies=["Triage", "Vitals"],
    )

    answers = {
        "domain_alignment": {"choice": "direct_domain_match"},
        "competency_depth": {"score": 3.5},  # 70%
        "seniority_level": {"score": 3.0},   # 60%
        "evidence_quality": {"score": 3.0},  # 60%
        "gate_0_rn_license": {"probability": 0.15},  # FAILED DEALBREAKER (< 0.40)
    }
    registry = {"gate_0_rn_license": {"name": "Active State RN License", "question": "Has RN license?"}}

    verdict = speculative_evaluator.evaluate(
        candidate_sections=candidate,
        answers=answers,
        gate_registry=registry,
    )

    assert verdict.overall_decision == "REJECT"
    assert verdict.veto_reason == "mandatory_dealbreaker_failed"
    assert verdict.fit_score <= 35.0
    assert len(verdict.failed_hard_gates) == 1
    assert verdict.failed_hard_gates[0].name == "Active State RN License"
    assert "missing mandatory requirement(s)" in verdict.summary_feedback


def test_speculative_gate_3_qualified_candidate_advancement():
    """Gate 3: Fully qualified candidate passing all gates achieves high fit score and ADVANCE verdict."""
    candidate = ResumeParsedSections(
        candidate_name="Sarah Connor, RN",
        professional_summary="Senior ICU Nurse with 5 years critical care.",
        work_experience=[
            WorkExperienceItem(
                employer="Hospital A",
                role_title="Staff Nurse",
                responsibilities_and_achievements=["Patient care in ICU."],
                tools_and_methods=["Ventilators", "Arterial Lines"],
            ),
            WorkExperienceItem(
                employer="Hospital B",
                role_title="Charge Nurse",
                responsibilities_and_achievements=["Supervised unit shifts."],
                tools_and_methods=["Epic", "CRRT"],
            ),
        ],
        education=[EducationItem(institution="Emory", degree_name="BSN")],
        core_competencies=["Ventilator Management", "Hemodynamic Monitoring", "Critical Drip Titration"],
        certifications_and_licenses=["Georgia RN License", "ACLS"],
    )

    answers = {
        "domain_alignment": {"choice": "direct_domain_match"},
        "competency_depth": {"score": 4.5},  # 90%
        "seniority_level": {"score": 4.0},   # 80%
        "evidence_quality": {"score": 4.0},  # 80%
        "gate_0_rn": {"probability": 0.95},
        "gate_1_acls": {"probability": 0.90},
    }
    registry = {
        "gate_0_rn": {"name": "RN License", "question": "Has RN?"},
        "gate_1_acls": {"name": "ACLS", "question": "Has ACLS?"},
    }

    verdict = speculative_evaluator.evaluate(
        candidate_sections=candidate,
        answers=answers,
        gate_registry=registry,
    )

    assert verdict.overall_decision == "ADVANCE"
    assert verdict.veto_reason is None
    assert verdict.fit_score >= 70.0
    assert len(verdict.failed_hard_gates) == 0
    assert len(verdict.passed_hard_gates) == 2


# ---------------------------------------------------------------------------
# 4. Dual Engine (Jev & Laya) Fan-Out Tests
# ---------------------------------------------------------------------------

import asyncio

def test_jev_client_evaluate_fanout():
    """Verifies that JevClient executes evaluate_fanout over candidate state with primitives."""
    async def _run():
        client = JevClient.get_instance()
        state = "CANDIDATE: John Doe, Senior Python Engineer with 6 years experience in FastAPI and AWS."
        questions = {
            "domain_alignment": Choice(
                instructions="Classify domain:",
                criteria={"core": "Software Engineer", "other": "Non-technical"},
            ),
            "seniority_level": Score(
                instructions="Rate seniority:",
                criteria=["L0", "L1", "L2", "L3", "L4", "L5"],
            ),
            "has_experience": Noul(instructions="Has 4+ years?"),
        }

        answers = await client.evaluate_fanout(state=state, questions=questions)
        assert isinstance(answers, dict)
        assert "domain_alignment" in answers
        assert "seniority_level" in answers
        assert "has_experience" in answers

    asyncio.run(_run())


def test_laya_client_evaluate_fanout():
    """Verifies that LayaClient executes evaluate_fanout with identical signature and schemas."""
    async def _run():
        client = LayaClient.get_instance()
        state = "CANDIDATE: Alice Smith, ICU Charge Nurse with 7 years clinical experience."
        questions = {
            "domain_alignment": Choice(
                instructions="Classify domain:",
                criteria={"nursing": "Clinical Nurse", "other": "Other"},
            ),
            "seniority_level": Score(
                instructions="Rate seniority:",
                criteria=["L0", "L1", "L2", "L3", "L4", "L5"],
            ),
            "has_license": Noul(instructions="Has RN License?"),
        }

        answers = await client.evaluate_fanout(state=state, questions=questions)
        assert isinstance(answers, dict)
        assert "domain_alignment" in answers
        assert "seniority_level" in answers
        assert "has_license" in answers

    asyncio.run(_run())

