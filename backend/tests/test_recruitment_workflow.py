"""
CareerLens AI - Automated Tests for Dual-Gate Rate Limiting, Database Deduplication,
Human-in-the-Loop Question Review, and Throttled Streaming Evaluation.
"""

import asyncio
import io
import json
import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.core.rate_limiter import DualGateLLMRateLimiter
from app.engines.question_factory.adapter import BlueprintToEngineAdapter
from app.main import app
from app.models.db.job_requisition import JobRequisition
from app.models.db.parsed_resume import ParsedResume
from app.models.domain.dynamic_blueprint import (
    AscendingAssessmentBlueprint,
    BackgroundClassificationBlueprint,
    EvaluationQuestionsBlueprint,
    MandatoryDealbreakerBlueprint,
)
from app.models.domain.resume_sections import (
    EducationItem,
    ResumeParsedSections,
    WorkExperienceItem,
)
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.recruitment_service import recruitment_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_dual_gate_rate_limiter_in_flight_exclusivity():
    """
    Verifies that DualGateLLMRateLimiter enforces mutual exclusion:
    At most 1 task is in-flight at any time, even if tasks take time.
    """
    async def _run():
        limiter = DualGateLLMRateLimiter(interval_seconds=0.1, post_call_cooldown=0.05)
        in_flight_tracker = []

        async def mock_llm_call(task_id: int):
            in_flight_tracker.append(limiter.in_flight)
            await asyncio.sleep(0.08)
            return task_id

        tasks = [limiter.execute(mock_llm_call, i) for i in range(3)]
        results = await asyncio.gather(*tasks)

        assert results == [0, 1, 2]
        # Every call when active must have seen exactly in_flight == 1
        assert all(val == 1 for val in in_flight_tracker)

    asyncio.run(_run())


def test_dual_gate_rate_limiter_slow_response_hazard():
    """
    Simulates the slow LLM hazard where an LLM call takes > interval:
    The next call must NOT execute in parallel, and must wait for completion + cooldown.
    """
    async def _run():
        limiter = DualGateLLMRateLimiter(interval_seconds=0.05, post_call_cooldown=0.05)
        execution_timeline = []

        async def slow_llm_call():
            execution_timeline.append("start_slow")
            await asyncio.sleep(0.12)  # Takes longer than interval (0.05s)
            execution_timeline.append("end_slow")
            return "slow_done"

        async def fast_llm_call():
            execution_timeline.append("start_fast")
            await asyncio.sleep(0.02)
            execution_timeline.append("end_fast")
            return "fast_done"

        task1 = asyncio.create_task(limiter.execute(slow_llm_call))
        await asyncio.sleep(0.01)  # Ensure task1 starts first
        task2 = asyncio.create_task(limiter.execute(fast_llm_call))

        await asyncio.gather(task1, task2)

        # Invariant: fast call must NOT start before slow call ends!
        assert execution_timeline == ["start_slow", "end_slow", "start_fast", "end_fast"]

    asyncio.run(_run())


def test_job_analysis_caching_and_deduplication():
    """
    Verifies that analyzing a JD creates a requisition, and repeated calls with the same JD
    return the cached result without duplicate LLM calls.
    """
    role = "Lead Distributed Systems Architect"
    jd = "Seeking a lead architect with 8+ years experience in distributed systems, Raft consensus, and high throughput microservices."

    response1 = client.post(
        "/api/v1/jobs/analyze",
        json={"role_title": role, "job_description": jd},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    job_id = data1["job_id"]
    assert "questions" in data1
    assert data1["is_reviewed"] is False

    # Second call with same role and JD must be cached
    response2 = client.post(
        "/api/v1/jobs/analyze",
        json={"role_title": role, "job_description": jd},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["job_id"] == job_id
    assert data2["cached"] is True


def test_mandatory_question_review_precondition_gate():
    """
    Verifies that candidate evaluation strictly blocks (HTTP 400) if questions have not been reviewed,
    and succeeds once the recruiter confirms review via PUT /api/v1/jobs/{job_id}/questions.
    """
    db = SessionLocal()
    try:
        # 1. Create a dummy requisition
        job = JobRepository.create(
            db=db,
            role_title="Senior ICU Nurse",
            job_description="ICU Nurse with 3+ years experience. Mandatory: RN License, BLS, ACLS.",
            blueprint_json=json.dumps(
                EvaluationQuestionsBlueprint(
                    role_title="Senior ICU Nurse",
                    seniority_target="Senior Staff Nurse",
                    domain_alignment=BackgroundClassificationBlueprint(
                        question="Classify nursing domain background:",
                        options={"direct_domain_match": "ICU", "adjacent_domain_transfer": "Med-Surg", "unrelated_background": "Other"},
                    ),
                    seniority_assessment=AscendingAssessmentBlueprint(
                        question="Rate nursing seniority:",
                        levels=["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
                    ),
                    competency_depth_assessment=AscendingAssessmentBlueprint(
                        question="Rate ICU clinical depth:",
                        levels=["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
                    ),
                    evidence_quality_assessment=AscendingAssessmentBlueprint(
                        question="Rate clinical evidence:",
                        levels=["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
                    ),
                    mandatory_dealbreakers=[
                        MandatoryDealbreakerBlueprint(name="Active RN License", question="Does candidate hold an active RN license?")
                    ],
                ).model_dump()
            ),
            is_reviewed=False,
        )
        job_id = job.id

        # 2. Create a dummy completed parsed resume
        sections = ResumeParsedSections(
            candidate_name="Nurse Sarah Jenkins",
            email="sarah@example.com",
            phone="555-1234",
            location="Houston, TX",
            professional_summary="Experienced ICU nurse with 5 years in acute care.",
            work_experience=[
                WorkExperienceItem(
                    employer="Methodist Hospital",
                    role_title="ICU Staff Nurse",
                    start_date="2019",
                    end_date="Present",
                    is_current=True,
                    responsibilities_and_achievements=["Ventilator management"],
                    tools_and_methods=["Mechanical Ventilation"],
                )
            ],
            core_competencies=["Mechanical Ventilation", "Hemodynamic Monitoring"],
            education=[EducationItem(degree_name="BSN", institution="UT Health", graduation_year=2018)],
            certifications_and_licenses=["RN License #12345", "BLS", "ACLS"],
        )
        resume = ResumeRepository.create(
            db=db,
            file_hash="dummy_hash_sarah_123",
            filename="sarah_jenkins.pdf",
            file_size_bytes=1024,
            status="completed",
            parsed_sections_json=json.dumps(sections.model_dump()),
        )
        resume_id = resume.id

        # 3. Attempt evaluation without review -> Must return 400 Bad Request
        eval_resp_blocked = client.post(
            f"/api/v1/jobs/{job_id}/evaluations",
            json={"resume_ids": [resume_id], "pipeline": "laya"},
        )
        assert eval_resp_blocked.status_code == 400
        assert "mandatory precondition" in eval_resp_blocked.json()["detail"].lower()

        # 4. Recruiter reviews questions and toggles is_mandatory
        review_payload = {
            "questions": {
                "domain_alignment": {
                    "name": "domain_alignment",
                    "type": "choice",
                    "primitive": "Choice",
                    "scale": "direct_domain_match, adjacent_domain_transfer, unrelated_background",
                    "instructions": "Classify clinical nursing background:",
                    "is_mandatory": False,
                },
                "Active RN License": {
                    "name": "Active RN License",
                    "type": "noul",
                    "primitive": "Noul",
                    "scale": "P(True)",
                    "instructions": "Does candidate hold an active RN license?",
                    "is_mandatory": True,  # Confirmed as mandatory dealbreaker
                },
            }
        }
        review_resp = client.put(f"/api/v1/jobs/{job_id}/questions", json=review_payload)
        assert review_resp.status_code == 200
        assert review_resp.json()["is_reviewed"] is True

        # 5. Now evaluation succeeds
        eval_resp_allowed = client.post(
            f"/api/v1/jobs/{job_id}/evaluations",
            json={"resume_ids": [resume_id], "pipeline": "laya"},
        )
        assert eval_resp_allowed.status_code == 200
        eval_data = eval_resp_allowed.json()
        assert eval_data["total_evaluated"] == 1
        assert eval_data["evaluations"][0]["candidate_name"] == "Nurse Sarah Jenkins"

    finally:
        db.close()


def test_granular_resume_details_endpoint():
    """
    Verifies that GET /api/v1/resumes/{resume_id} returns all 6 canonical sections.
    """
    db = SessionLocal()
    try:
        sections = ResumeParsedSections(
            candidate_name="Marcus Vance",
            email="marcus@tech.io",
            phone="555-8888",
            location="Seattle, WA",
            professional_summary="Principal distributed systems engineer.",
            work_experience=[
                WorkExperienceItem(
                    employer="CloudScale Inc",
                    role_title="Lead Architect",
                    start_date="2020",
                    end_date="Present",
                    is_current=True,
                    responsibilities_and_achievements=["Architected multi-region consensus protocol handling 100k rps."],
                    tools_and_methods=["Go", "Raft", "Kubernetes"],
                )
            ],
            core_competencies=["Distributed Consensus", "Go", "Kubernetes", "gRPC"],
            education=[EducationItem(degree_name="MS Computer Science", institution="UW", graduation_year=2016)],
            certifications_and_licenses=["AWS Solutions Architect Professional"],
        )
        resume = ResumeRepository.create(
            db=db,
            file_hash="dummy_hash_marcus_vance",
            filename="marcus_vance.pdf",
            file_size_bytes=2048,
            status="completed",
            parsed_sections_json=json.dumps(sections.model_dump()),
        )
        resume_id = resume.id

        resp = client.get(f"/api/v1/resumes/{resume_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["resume_id"] == resume_id
        assert data["filename"] == "marcus_vance.pdf"
        assert data["status"] == "completed"
        assert data["parsed_sections"]["candidate_name"] == "Marcus Vance"
        assert len(data["parsed_sections"]["work_experience"]) == 1
        assert "AWS Solutions Architect Professional" in data["parsed_sections"]["certifications_and_licenses"]

    finally:
        db.close()


def test_resume_upload_pdf_byte_hash_deduplication():
    """
    Verifies that uploading the exact same PDF bytes returns a cached record with 0s delay.
    """
    # Create mock PDF content
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (Test Resume) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

    response1 = client.post(
        "/api/v1/resumes/upload",
        files=[("files", ("test_candidate.pdf", pdf_bytes, "application/pdf"))],
    )
    assert response1.status_code == 202
    data1 = response1.json()
    assert data1["total_uploaded"] == 1
    resume_id = data1["resumes"][0]["resume_id"]

    # Manually mark as completed in DB to simulate finished parse
    db = SessionLocal()
    try:
        resume = ResumeRepository.get_by_id(db, resume_id)
        assert resume is not None
        resume.status = "completed"
        db.commit()
    finally:
        db.close()

    # Re-uploading identical file bytes must return cached
    response2 = client.post(
        "/api/v1/resumes/upload",
        files=[("files", ("test_candidate.pdf", pdf_bytes, "application/pdf"))],
    )
    assert response2.status_code == 202
    data2 = response2.json()
    assert data2["cached_count"] == 1
    assert data2["resumes"][0]["status"] == "cached"
    assert data2["resumes"][0]["eta_seconds"] == 0


def test_streaming_evaluation_endpoint():
    """
    Verifies that POST /api/v1/jobs/{job_id}/evaluations/stream returns an SSE stream.
    """
    db = SessionLocal()
    try:
        job = JobRepository.create(
            db=db,
            role_title="Backend Developer",
            job_description="Python developer with FastAPI experience.",
            blueprint_json=json.dumps(
                EvaluationQuestionsBlueprint(
                    role_title="Backend Developer",
                    seniority_target="Mid-Level",
                    domain_alignment=BackgroundClassificationBlueprint(
                        question="Classify domain:",
                        options={"direct_domain_match": "Python", "adjacent_domain_transfer": "Java", "unrelated_background": "Other"},
                    ),
                    seniority_assessment=AscendingAssessmentBlueprint(
                        question="Rate seniority:",
                        levels=["L0", "L1", "L2", "L3", "L4", "L5"],
                    ),
                    competency_depth_assessment=AscendingAssessmentBlueprint(
                        question="Rate competency:",
                        levels=["L0", "L1", "L2", "L3", "L4", "L5"],
                    ),
                    evidence_quality_assessment=AscendingAssessmentBlueprint(
                        question="Rate evidence:",
                        levels=["L0", "L1", "L2", "L3", "L4", "L5"],
                    ),
                    mandatory_dealbreakers=[],
                ).model_dump()
            ),
            is_reviewed=True,  # Mark as reviewed
        )
        job_id = job.id

        sections = ResumeParsedSections(
            candidate_name="Alex Rivera",
            professional_summary="Backend engineer specializing in FastAPI and Python.",
            core_competencies=["Python", "FastAPI", "PostgreSQL"],
        )
        resume = ResumeRepository.create(
            db=db,
            file_hash="dummy_hash_alex_rivera",
            filename="alex_rivera.pdf",
            file_size_bytes=512,
            status="completed",
            parsed_sections_json=json.dumps(sections.model_dump()),
        )
        resume_id = resume.id

        with client.stream(
            "POST",
            f"/api/v1/jobs/{job_id}/evaluations/stream",
            json={"resume_ids": [resume_id], "pipeline": "laya"},
        ) as stream_resp:
            assert stream_resp.status_code == 200
            assert "text/event-stream" in stream_resp.headers["content-type"]
            events = []
            for chunk in stream_resp.iter_lines():
                if chunk.startswith("event:"):
                    events.append(chunk.replace("event:", "").strip())

            assert "started" in events
            assert "candidate_evaluated" in events
            assert "completed" in events

    finally:
        db.close()
