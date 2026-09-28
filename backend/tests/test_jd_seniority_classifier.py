import pytest
from app.tools.candidate_scorer import ROLE_WEIGHTS
from app.extraction.jd_extractor import extract_job_profile


def test_role_weights_structure():
    assert "beginner" in ROLE_WEIGHTS
    assert "mid_level" in ROLE_WEIGHTS
    assert "senior" in ROLE_WEIGHTS

    for tier, weights in ROLE_WEIGHTS.items():
        assert set(weights.keys()) == {"technical", "experience", "domain", "education", "evidence"}
        assert round(sum(weights.values()), 2) == 1.00


def test_classify_jd_seniority_beginner():
    jd = "Junior Software Engineer / Intern. 0-1 years of experience, fresh college graduates welcome."
    profile = extract_job_profile(jd, job_role="Junior Software Engineer")
    assert profile.seniority_score <= 1.5
    assert "Junior" in profile.seniority_label or "Entry" in profile.seniority_label or "Intern" in profile.seniority_label


def test_classify_jd_seniority_senior():
    jd = "Staff / Principal Distributed Systems Architect. Requires 8+ years experience leading engineering teams."
    profile = extract_job_profile(jd, job_role="Principal Architect")
    assert profile.seniority_score >= 3.0
    assert "Senior" in profile.seniority_label or "Lead" in profile.seniority_label


def test_classify_jd_seniority_mid_level():
    jd = "Full Stack Software Engineer with 3-4 years experience building React and Python applications."
    profile = extract_job_profile(jd, job_role="Software Engineer")
    assert 1.5 <= profile.seniority_score <= 3.5
