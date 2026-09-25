import pytest
from app.core.decision_engine import LayaDecisionEngine, ROLE_WEIGHTS


def test_role_weights_structure():
    assert "beginner" in ROLE_WEIGHTS
    assert "mid_level" in ROLE_WEIGHTS
    assert "senior" in ROLE_WEIGHTS

    for tier, weights in ROLE_WEIGHTS.items():
        assert set(weights.keys()) == {"technical", "experience", "domain", "education", "evidence"}
        assert round(sum(weights.values()), 2) == 1.00


def test_classify_jd_seniority_beginner():
    engine = LayaDecisionEngine.get_instance()
    jd = "Junior Software Engineer / Intern. 0-1 years of experience, fresh college graduates welcome."
    result = engine.classify_jd_seniority(jd)
    assert result["seniority_tier"] == "beginner"
    assert result["seniority_label"] in ("Junior / Entry-Level", "Beginner")
    assert result["weights"] == ROLE_WEIGHTS["beginner"]


def test_classify_jd_seniority_senior():
    engine = LayaDecisionEngine.get_instance()
    jd = "Staff / Principal Distributed Systems Architect. Requires 8+ years experience leading engineering teams."
    result = engine.classify_jd_seniority(jd)
    assert result["seniority_tier"] == "senior"
    assert result["seniority_label"] in ("Senior / Lead", "Senior")
    assert result["weights"] == ROLE_WEIGHTS["senior"]


def test_classify_jd_seniority_mid_level():
    engine = LayaDecisionEngine.get_instance()
    jd = "Full Stack Software Engineer with 3-4 years experience building React and Python applications."
    result = engine.classify_jd_seniority(jd)
    assert result["seniority_tier"] == "mid_level"
    assert result["weights"] == ROLE_WEIGHTS["mid_level"]
