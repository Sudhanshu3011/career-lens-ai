import pytest
from app.engines.evaluation.candidate_scorer import score_resume_against_jd


def test_score_resume_against_jd():
    resume_data = {
        "tech_skills": ["Python", "PyTorch", "FastAPI", "Docker", "PostgreSQL"],
        "tools_and_platforms": ["Docker", "Git"],
        "domains": ["AI / Machine Learning", "Backend & Distributed Systems"],
        "experience": "AI engineer with 3 years building PyTorch deep learning models and deploying FastAPI microservices.",
        "summary": "Proficient in Python, PyTorch, Docker, and REST APIs.",
    }
    jd_text = (
        "Seeking an AI / ML Engineer with 2+ years experience in Python, PyTorch, and FastAPI. "
        "Experience containerizing services with Docker is required."
    )

    eval_res = score_resume_against_jd(resume_data, jd_text)

    assert eval_res["final_score"] > 5.0
    assert "technical_overlap" in eval_res
    overlap = eval_res["technical_overlap"]
    assert "Python" in overlap["matched_skills"]
    assert "PyTorch" in overlap["matched_skills"]
    assert "FastAPI" in overlap["matched_skills"]
    assert overlap["skill_overlap_percentage"] >= 60.0
    assert "breakdown" in eval_res
    assert eval_res["breakdown"]["technical_requirements"] > 50
    assert "seniority_tier" in eval_res
    assert "role_weights" in eval_res
    assert "parameter_evaluations" in eval_res
    assert "high_hits_count" in eval_res
    assert "total_weighted_probability" in eval_res
    assert "penalty_applied" in eval_res
