import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.db.session import AnalysisSession
from app.services.session_service import SessionService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_session_service_pipeline_steps(db_session):
    resume_text = """
    John Doe
    Email: john@example.com | Phone: 9876543210
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 6 years building microservices with Python, FastAPI, and PostgreSQL.
    SKILLS
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, React
    EXPERIENCE
    Backend Engineer at TechCorp (2020 - Present)
    - Built REST APIs handling 10k RPS using FastAPI and Redis caching.
    EDUCATION
    B.Tech in Computer Science, IIT Delhi (2016 - 2020)
    """
    sample_jd = """
    Senior Python Developer
    Requirements:
    - 5+ years experience with Python and FastAPI
    - Strong database skills with PostgreSQL and Redis
    - Containerization with Docker and Kubernetes
    """

    session = AnalysisSession(
        resume_filename="john_doe.pdf",
        extracted_text=resume_text,
        job_description=sample_jd,
        status="pending",
        current_step=1,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    # Step 1: Parse (Deterministic layout parser)
    parse_res = SessionService.execute_step_1_parse(db_session, session.id)
    assert parse_res is not None
    assert "summary" in parse_res or "skills" in parse_res or "experience" in parse_res
    assert session.status == "parsed"
    assert session.current_step == 2

    # Step 2: Skills (Deterministic skill ontology)
    skills_res = SessionService.execute_step_2_skills(db_session, session.id)
    assert "technical_skills" in skills_res
    assert any("python" in s.lower() for s in skills_res["technical_skills"])
    assert session.status == "skills_extracted"
    assert session.current_step == 3

    # Step 3: Decision (Calibrated candidate fit scoring)
    decision_res = SessionService.execute_step_3_decision(db_session, session.id)
    assert "final_score" in decision_res
    assert "overall_decision" in decision_res
    assert decision_res["final_score"] > 0
    assert session.status == "decision_computed"
    assert session.current_step == 4

    # Step 4: Feedback (Diagnostics state)
    feedback_res = SessionService.execute_step_4_feedback(db_session, session.id)
    assert "feedback" in feedback_res
    assert session.status == "feedback_ready"
    assert session.current_step == 5

    # Step 5: Scorecard summary (Calibrated fit evaluation)
    jobs_res = SessionService.execute_step_5_jobs(db_session, session.id)
    assert "scorecard" in jobs_res
    assert jobs_res["scorecard"]["final_score"] > 0
    assert session.status == "completed"


def test_session_repository_crud(db_session):
    from app.repositories.session_repository import SessionRepository

    sess = SessionRepository.create(
        db=db_session,
        filename="alice_resume.pdf",
        extracted_text="Alice Doe, Python backend engineer with 4 years experience.",
        job_description="Python engineer wanted.",
    )
    assert sess.id is not None
    assert sess.status == "pending"

    retrieved = SessionRepository.get_by_id(db_session, sess.id)
    assert retrieved is not None
    assert retrieved.resume_filename == "alice_resume.pdf"

    recent = SessionRepository.list_recent(db_session, limit=5)
    assert len(recent) >= 1
    assert any(s.id == sess.id for s in recent)

    sess.status = "completed"
    saved = SessionRepository.save(db_session, sess)
    assert saved.status == "completed"
