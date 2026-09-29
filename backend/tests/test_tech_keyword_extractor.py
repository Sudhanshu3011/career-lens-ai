import time
import pytest
from app.engines.extraction.tech_keywords import extract_tech_keywords


def test_special_symbols_extraction():
    text = (
        "Core technologies: C++, C#, .NET Core, CI/CD with GitHub Actions and Docker."
    )
    res = extract_tech_keywords(text)
    skills = res["extracted_skills"]

    assert "C++" in skills
    assert "C#" in skills
    assert "ASP.NET Core" in skills
    assert "CI/CD" in skills
    assert "Docker" in skills
    assert "Git" in skills or "GitHub Actions" in skills


def test_synonym_normalization():
    text = "Deploying microservices on k8s with postgres and reactjs frontend."
    res = extract_tech_keywords(text)
    skills = res["extracted_skills"]

    assert "Kubernetes" in skills  # normalized from k8s
    assert "PostgreSQL" in skills  # normalized from postgres
    assert "React" in skills  # normalized from reactjs
    assert "Microservices" in skills


def test_domain_categorization():
    text = "Python, PyTorch, LangChain, PostgreSQL, React, AWS, Docker."
    res = extract_tech_keywords(text)
    by_domain = res["skills_by_domain"]

    assert "Python" in by_domain.get("languages", [])
    assert "PyTorch" in by_domain.get("ai_ml_data_science", [])
    assert "LangChain" in by_domain.get("genai_llms", [])
    assert "PostgreSQL" in by_domain.get("databases", [])
    assert "React" in by_domain.get("frontend", [])
    assert "AWS" in by_domain.get("cloud_devops", [])


def test_skills_extraction_aiml():
    text = """
    AI Engineer with deep expertise in PyTorch, TensorFlow, Scikit-Learn, YOLO,
    OpenCV, LangChain, RAG pipelines, Vector Databases, Fine-Tuning, and Python.
    """
    res = extract_tech_keywords(text)
    skills = res["extracted_skills"]
    assert "PyTorch" in skills
    assert "TensorFlow" in skills
    assert "Python" in skills
    assert "LangChain" in skills
    assert "extracted_skills" in res
    assert "skills_by_domain" in res


def test_skills_extraction_frontend():
    text = """
    Frontend Developer specializing in React, Next.js, TypeScript, Tailwind CSS,
    Redux Toolkit, Zustand, HTML5, and CSS3.
    """
    res = extract_tech_keywords(text)
    skills = res["extracted_skills"]
    assert "React" in skills
    assert "Next.js" in skills
    assert "TypeScript" in skills
    assert "Tailwind CSS" in skills


def test_execution_speed_benchmark():
    text = """
    Senior Full-Stack Engineer with 5+ years experience building distributed systems in Go and Python.
    Experienced in React, Next.js, TypeScript, PostgreSQL, Redis, Apache Kafka, Docker, Kubernetes,
    AWS Lambda, S3, CI/CD, and Terraform. Developed microservices with gRPC and REST APIs.
    """
    start = time.perf_counter()
    res = extract_tech_keywords(text)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert res["total_skills_count"] >= 12
    assert elapsed_ms < 50.0  # Typically 2-5ms
