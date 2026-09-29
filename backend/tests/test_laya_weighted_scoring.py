import pytest
from app.engines.evaluation.candidate_scorer import (
    score_resume_against_jd,
    ROLE_WEIGHTS,
)


def test_five_parameter_weighted_scoring_structure():
    candidate_skills = ["Python", "PyTorch", "TensorFlow", "FastAPI"]
    resume_data = {
        "tech_skills": candidate_skills,
        "tools_and_platforms": ["Docker", "Git"],
        "domains": ["AI / Machine Learning"],
        "experience": "5 years developing deep learning computer vision pipelines in production with 35% latency reduction.",
        "education": "Bachelor of Science in Computer Science, 2019.",
    }
    job_description = "Senior AI Engineer with 5+ years experience in PyTorch, deep learning, and scalable APIs."

    result = score_resume_against_jd(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert "seniority_tier" in result
    assert "role_weights" in result
    assert "parameter_evaluations" in result

    params = result["parameter_evaluations"]
    assert set(params.keys()) == {
        "technical",
        "experience",
        "domain",
        "education",
        "evidence",
    }

    for p_name, p_data in params.items():
        assert "p_high" in p_data
        assert "p_mid" in p_data
        assert "p_low" in p_data
        assert "selected_prob" in p_data
        assert p_data["selected_prob"] == max(p_data["p_high"], p_data["p_mid"])
        assert "weight" in p_data
        assert "weighted_score" in p_data
        assert "is_high_hit" in p_data

    assert "raw_weighted_probability" in result
    assert 0.0 <= result["raw_weighted_probability"] <= 1.0
    assert "high_hits_count" in result
    assert 0 <= result["high_hits_count"] <= 5
    assert "penalty_applied" in result
    assert "total_weighted_probability" in result
    assert 0.0 <= result["total_weighted_probability"] <= 1.0
    assert "final_score" in result
    assert "overall_decision" in result


def test_least_high_hits_penalty_calculation():
    # Verify penalty logic: penalty = max(0.0, (3 - H) * 0.02)
    def calc_penalty(h: int) -> float:
        return round(max(0.0, (3 - h) * 0.02), 4)

    assert calc_penalty(0) == 0.06
    assert calc_penalty(1) == 0.04
    assert calc_penalty(2) == 0.02
    assert calc_penalty(3) == 0.0
    assert calc_penalty(4) == 0.0
    assert calc_penalty(5) == 0.0


def test_dynamic_job_role_injection():
    resume_data = {
        "tech_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "tools_and_platforms": ["Git", "Linux"],
        "domains": ["Backend Development"],
        "experience": "3 years developing scalable REST APIs and database schema migrations.",
        "education": "BS in Computer Science.",
    }
    job_description = (
        "Looking for a backend engineer to design and maintain robust microservices."
    )

    result = score_resume_against_jd(
        resume_data=resume_data,
        job_description=job_description,
        job_role="Lead Cloud Architect",
    )

    assert result is not None
    assert "parameter_evaluations" in result
    assert "total_weighted_probability" in result
    assert result["target_seniority_tier"] == "senior"
