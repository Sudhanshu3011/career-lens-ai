import time
import pytest
from app.tools.deterministic_parser import (
    parse_resume_from_text,
    extract_contact_info,
    extract_candidate_name,
    classify_section_header,
)

SAMPLE_RESUME_TEXT = """
Alex Rivera
San Francisco, CA | (555) 123-4567 | alex.rivera@example.com
linkedin.com/in/alex-rivera-dev | github.com/alexrivera

PROFESSIONAL SUMMARY
Senior Full-Stack AI Engineer with 6+ years of experience architecting high-throughput distributed microservices, LLM agent workflows, and reactive frontend platforms. Expert in Python, FastAPI, and Docker.

TECHNICAL SKILLS
- Programming Languages: Python, TypeScript, Go, SQL
- Frameworks & Libraries: FastAPI, Next.js, PyTorch, LangChain, React
- Cloud & Infrastructure: Docker, Kubernetes, AWS, PostgreSQL, Redis, CI/CD

WORK EXPERIENCE
Senior Platform Engineer | TechNova Solutions
January 2022 - Present | San Francisco, CA
- Architected multi-agent streaming pipelines using FastAPI and Redis Pub/Sub, reducing response latency by 45%.
- Deployed fault-tolerant microservices across AWS ECS clusters serving 2.5M daily active users.
- Mentored 6 junior engineers and enforced 100% test coverage policies for core financial transactions.

Software Engineer | Apex Cloud Systems
June 2018 - December 2021 | Austin, TX
- Developed RESTful backend APIs in Python and Django handling 15,000 requests per second.
- Optimized slow PostgreSQL queries and index structures, improving database throughput by 32%.
- Integrated Stripe billing and webhook listeners with automated idempotency keys.

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
Graduated: May 2018

KEY PROJECTS
Distributed Vector Cache: High-performance in-memory similarity search engine built in Python and C extensions.
Autonomous Job Matcher: Multi-agent scraper matching candidate resumes against live job openings.

CERTIFICATIONS & LICENSES
- AWS Certified Solutions Architect - Associate
- Certified Kubernetes Administrator (CKA)
"""


def test_contact_info_extraction():
    contact = extract_contact_info(SAMPLE_RESUME_TEXT)
    assert contact["email"] == "alex.rivera@example.com"
    assert "555" in contact["phone"]
    assert "alex-rivera-dev" in contact["linkedin"]
    assert "alexrivera" in contact["github"]


def test_candidate_name_extraction():
    lines = ["Alex Rivera", "San Francisco, CA | (555) 123-4567"]
    name = extract_candidate_name(lines)
    assert name == "Alex Rivera"


def test_header_classification():
    # Valid headers
    sec, conf = classify_section_header("WORK EXPERIENCE")
    assert sec == "experience"
    assert conf >= 60.0

    sec, conf = classify_section_header("TECHNICAL SKILLS")
    assert sec == "skills"
    assert conf >= 60.0

    sec, conf = classify_section_header("EDUCATION")
    assert sec == "education"
    assert conf >= 60.0

    sec, conf = classify_section_header("CERTIFICATIONS & LICENSES")
    assert sec == "certifications"
    assert conf >= 60.0

    # Negative cases: bullet points and action sentences must NOT be classified as headers
    sec, conf = classify_section_header("- Architected multi-agent streaming pipelines using FastAPI")
    assert sec is None
    assert conf == 0.0

    sec, conf = classify_section_header("Experienced software engineer with 5 years of background.")
    assert sec is None
    assert conf == 0.0


def test_full_text_resume_parsing():
    start_time = time.perf_counter()
    parsed = parse_resume_from_text(SAMPLE_RESUME_TEXT)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Verification of parsed sections
    assert parsed["candidate_name"] == "Alex Rivera"
    assert "Senior Full-Stack AI Engineer" in parsed["summary"]
    assert "Python, TypeScript" in parsed["skills"]
    assert "TechNova Solutions" in parsed["experience"]
    assert "University of California, Berkeley" in parsed["education"]
    assert "Distributed Vector Cache" in parsed["projects"]
    assert "AWS Certified Solutions Architect" in parsed["certifications"]
    assert parsed["contact_info"]["email"] == "alex.rivera@example.com"

    # Must be sub-100ms (zero-LLM speed)
    assert elapsed_ms < 100.0  # Typically 2-5ms


def test_real_aiml_pdf_parsing():
    import os
    from app.tools.deterministic_parser import parse_resume_from_pdf

    pdf_path = "/tmp/AIML_resume.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "/tmp/resume/AIML_resume.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "AIML_resume.pdf"

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        parsed = parse_resume_from_pdf(pdf_bytes)
        assert parsed["candidate_name"] == "Sudhanshu Shekhar"
        assert parsed["contact_info"]["email"] == "sudhanshushekarkumar@gmail.com"
        assert "9104667657" in parsed["contact_info"]["phone"]
        assert "Vishwakarma" in parsed["education"]
        assert "Python" in parsed["skills"]
        assert "DRC Systems" in parsed["experience"]
        assert "Artha Analytics" in parsed["projects"]
        assert "Scaler" in parsed["certifications"]


def test_indian_5plus5_phone_format():
    text = "Chirag Chatwani | +91 95581 04404 | contact@chirag45.dev | chirag45.dev"
    contact = extract_contact_info(text)
    assert contact["phone"] == "+91 95581 04404"
    assert contact["email"] == "contact@chirag45.dev"
    assert contact["portfolio"] == "chirag45.dev"


def test_academic_table_header_classification():
    sec, conf = classify_section_header("Examination University Institute Year CPI/%")
    assert sec == "education"
    assert conf >= 65.0


def test_multi_column_resume_parsing():
    import os
    from app.tools.deterministic_parser import parse_resume_from_pdf

    pdf_path = "/tmp/resume/adarsh_ambastha.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        parsed = parse_resume_from_pdf(pdf_bytes)
        assert parsed["candidate_name"] == "ADARSH AMBASTHA"
        assert len(parsed["summary"]) > 0
        assert "Deep Learning" in parsed["skills"]
        assert "Tender AI" in parsed["projects"]
        assert "Master of Science" in parsed["education"]
        assert parsed["contact_info"]["portfolio"] == "www.drcsystems.com"


