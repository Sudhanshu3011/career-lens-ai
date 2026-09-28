"""
CareerLens AI - TypeSafe System One Architecture Unit Tests
Validates Choice, Score, and Noul primitives, structured JobProfile, hard gates, and composite decisions.
"""

import pytest
from app.jev.client import jev_client
from app.jev.rubric import RESUME_RUBRIC_V1, seniority_score_to_label
from app.jev.questions import build_jd_questions, build_requirement_questions
from app.models.job_profile import JobProfile, RequirementItem
from app.models.candidate_profile import CandidateProfile, ResumeBlock
from app.models.evidence import Evidence, EvidenceAssessment
from app.evaluation.seniority_evaluator import evaluate_seniority_gap, compute_seniority_fit_percentage
from app.evaluation.composite_score import calculate_composite_decision
from app.extraction.jd_extractor import extract_job_profile


def test_jev_primitives_structure():
    """Validates that Jev client returns valid Choice, Score, and Noul structures."""
    state = {"text": "Senior Machine Learning Engineer with 6 years experience deploying PyTorch models."}
    questions = {
        "seniority": {
            "type": "score",
            "instructions": "Rate candidate seniority.",
            "criteria": RESUME_RUBRIC_V1["seniority_levels"],
        },
        "has_pytorch": {
            "type": "noul",
            "instructions": "Does the candidate have verified PyTorch experience?",
        },
        "role_family": {
            "type": "choice",
            "instructions": "Identify the primary role family.",
            "criteria": RESUME_RUBRIC_V1["role_families"],
        }
    }
    answers = jev_client.predict(state, questions)

    assert "seniority" in answers
    assert answers["seniority"]["type"] == "score"
    assert 0.0 <= answers["seniority"]["score"] <= 6.0

    assert "has_pytorch" in answers
    assert answers["has_pytorch"]["type"] == "noul"
    assert 0.0 <= answers["has_pytorch"]["noul"] <= 1.0

    assert "role_family" in answers
    assert answers["role_family"]["type"] == "choice"
    assert answers["role_family"]["choice"] in RESUME_RUBRIC_V1["role_families"]


def test_seniority_gap_continuous_calculation():
    """Validates that continuous seniority gap is calculated accurately via subtraction."""
    # Senior applicant applying to Junior requisition -> EXCEEDS
    assessment_exceeds = evaluate_seniority_gap(jd_score=1.5, candidate_score=3.5)
    assert assessment_exceeds.seniority_gap == 2.0
    assert assessment_exceeds.alignment_label == "EXCEEDS"

    # Junior applicant applying to Senior requisition -> GAP
    assessment_gap = evaluate_seniority_gap(jd_score=3.8, candidate_score=1.2)
    assert assessment_gap.seniority_gap == -2.6
    assert assessment_gap.alignment_label == "GAP"

    # Mid applicant applying to Mid requisition -> ALIGNED
    assessment_aligned = evaluate_seniority_gap(jd_score=2.2, candidate_score=2.5)
    assert abs(assessment_aligned.seniority_gap) <= 0.8
    assert assessment_aligned.alignment_label == "ALIGNED"


def test_hard_requirement_gate_veto():
    """Validates that failing a mandatory hard requirement vetoes candidate to REJECT."""
    seniority = evaluate_seniority_gap(jd_score=2.0, candidate_score=2.2)
    
    # Candidate passed all high scores, but failed the mandatory AWS hard gate
    assessment = EvidenceAssessment(
        requirement_name="AWS",
        is_hard_requirement=True,
        satisfied_probability=0.20, # < 0.40 gate threshold
        direct_evidence_probability=0.10,
        evidence_strength=1.0,
        relevance_score=1.0,
        confidence=0.85,
        verdict="missing",
    )
    
    from app.models.decision import HardRequirementGate
    gate = HardRequirementGate(
        requirement_name="AWS",
        passed=False,
        probability=0.20,
        confidence=0.85,
        reason="Critical hard requirement 'AWS' unmet (P=0.20 < 0.40).",
    )

    decision = calculate_composite_decision(
        candidate_id="cand-1",
        candidate_name="Test Candidate",
        seniority=seniority,
        assessments=[assessment],
        hard_gates=[gate],
        all_hard_gates_passed=False,
        technical_overlap_pct=85.0,
        domain_overlap_pct=80.0,
        has_education=True,
    )

    assert decision.overall_decision == "REJECT"
    assert not decision.hard_gates_passed
    assert "AWS" in decision.failed_hard_gates
    assert any("Hard gate failure" in flag for flag in decision.review_flags)


def test_extract_job_profile_structured_normalization():
    """Validates that extract_job_profile produces a complete JobProfile."""
    jd_text = (
        "Senior Backend Engineer. Must have: Python, FastAPI, Docker, and AWS. "
        "Minimum 5 years of professional experience required."
    )
    profile = extract_job_profile(job_description=jd_text, job_role="Senior Backend Engineer")

    assert profile.role_title == "Senior Backend Engineer"
    assert profile.seniority_score >= 2.0
    assert "Python" in profile.required_skills or "FastAPI" in profile.required_skills
    assert len(profile.hard_requirements) > 0


def test_official_typesafe_sdk_primitives():
    """Validates typesafe-sdk Choice, Score, Noul invocation with client.system_one()."""
    from typesafe_sdk import Choice, Noul, Score
    ticket = "Senior Backend Engineer with 5 years of Python and FastAPI."
    questions = {
        "department": Choice(
            instructions="Which team should handle this",
            criteria={
                "billing": "Payment issues",
                "backend": "Python, API issues",
            },
        ),
        "seniority": Score(
            instructions="Rate seniority",
            criteria=["Junior", "Mid", "Senior"],
        ),
        "is_urgent": Noul(
            instructions="The message conveys urgency",
        ),
    }
    answers = jev_client.system_one(state=ticket, questions=questions)
    assert "department" in answers
    assert answers["department"]["choice"] in ("backend", "billing")
    assert "seniority" in answers
    assert 0 <= answers["seniority"]["score"] <= 2
    assert "is_urgent" in answers
