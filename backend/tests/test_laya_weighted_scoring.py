import pytest
from app.core.decision_engine import LayaDecisionEngine, ROLE_WEIGHTS


def test_five_parameter_weighted_scoring_structure():
    engine = LayaDecisionEngine.get_instance()
    candidate_skills = {
        "technical_skills": ["Python", "PyTorch", "TensorFlow", "FastAPI"],
        "tools_and_platforms": ["Docker", "Git"],
        "domains": ["AI / Machine Learning"],
    }
    experience_text = "5 years developing deep learning computer vision pipelines in production with 35% latency reduction."
    education_text = "Bachelor of Science in Computer Science, 2019."
    job_description = "Senior AI Engineer with 5+ years experience in PyTorch, deep learning, and scalable APIs."

    result = engine.evaluate_resume_match(
        candidate_skills=candidate_skills,
        experience_text=experience_text,
        job_description=job_description,
        education_text=education_text,
    )

    assert "seniority_tier" in result
    assert "role_weights" in result
    assert "parameter_evaluations" in result

    params = result["parameter_evaluations"]
    assert set(params.keys()) == {"technical", "experience", "domain", "education", "evidence"}

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
    engine = LayaDecisionEngine.get_instance()

    # Verify penalty logic: penalty = max(0.0, (3 - H) * 0.02)
    assert engine._calculate_high_hits_penalty(0) == 0.06
    assert engine._calculate_high_hits_penalty(1) == 0.04
    assert engine._calculate_high_hits_penalty(2) == 0.02
    assert engine._calculate_high_hits_penalty(3) == 0.0
    assert engine._calculate_high_hits_penalty(4) == 0.0
    assert engine._calculate_high_hits_penalty(5) == 0.0


def test_dynamic_job_role_injection():
    engine = LayaDecisionEngine.get_instance()
    candidate_skills = {
        "technical_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "tools_and_platforms": ["Git", "Linux"],
        "domains": ["Backend Development"],
    }
    experience_text = "3 years developing scalable REST APIs and database schema migrations."
    education_text = "BS in Computer Science."
    job_description = "Looking for a backend engineer to design and maintain robust microservices."

    # Test with explicit job_role
    result = engine.evaluate_resume_match(
        candidate_skills=candidate_skills,
        experience_text=experience_text,
        job_description=job_description,
        education_text=education_text,
        job_role="Lead Cloud Architect",
    )

    assert result is not None
    assert "parameter_evaluations" in result
    assert "total_weighted_probability" in result


def test_classify_jd_seniority_with_role():
    engine = LayaDecisionEngine.get_instance()

    # Role cue triggers beginner
    res_beg = engine.classify_jd_seniority(
        job_description="Develop web features and fix UI bugs.",
        job_role="Junior Frontend Intern",
    )
    assert res_beg["seniority_tier"] == "beginner"

    # Role cue triggers senior
    res_sr = engine.classify_jd_seniority(
        job_description="Design high throughput event streaming architecture.",
        job_role="Principal Distributed Systems Architect",
    )
    assert res_sr["seniority_tier"] == "senior"


def test_classify_candidate_seniority():
    engine = LayaDecisionEngine.get_instance()

    # Candidate with senior experience
    cand_sr = engine.classify_candidate_seniority(
        experience_text="2016 - 2024: Principal Architect leading distributed cloud infrastructure teams.",
        summary_text="Seasoned engineering leader with 8+ years hands-on experience.",
    )
    assert cand_sr["seniority_tier"] in ("senior", "mid_level")
    assert cand_sr["decision_source"] in ("laya_model", "deterministic_fallback")

    # Candidate with beginner / intern background
    cand_jr = engine.classify_candidate_seniority(
        experience_text="Summer 2024: Software Engineering Intern working on bug fixes and automated tests.",
        summary_text="Recent computer science graduate eager to learn.",
    )
    assert cand_jr["seniority_tier"] in ("beginner", "mid_level")
    assert cand_jr["decision_source"] in ("laya_model", "deterministic_fallback")


