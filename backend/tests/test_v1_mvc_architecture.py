"""
CareerLens AI - V1 MVC Architecture & Contract Tests
Verifies the clean, modular FastAPI architecture imports, schemas, endpoints, and services.
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_v1_architecture_canonical_imports():
    """Verify that all canonical imports from the active universal architecture succeed."""
    # 1. API & Routing
    from app.api.v1.router import api_router
    from app.api.v1.endpoints.jobs import router as jobs_router
    from app.api.v1.endpoints.resumes import router as resumes_router
    from app.api.v1.endpoints.analysis import router as ana_router
    from app.api.dependencies import get_db

    assert api_router is not None
    assert jobs_router is not None
    assert resumes_router is not None
    assert ana_router is not None
    assert get_db is not None

    # 2. Core
    from app.core.database import Base, SessionLocal, engine, init_db
    from app.core.validators import validate_pdf, validate_pdf_metadata

    assert Base is not None
    assert SessionLocal is not None
    assert engine is not None
    assert init_db is not None
    assert validate_pdf is not None

    # 3. Models (Database vs Clean Domain)
    from app.models.db.job_requisition import JobRequisition
    from app.models.db.parsed_resume import ParsedResume
    from app.models.db.candidate_evaluation import CandidateEvaluation
    from app.models.domain.resume_sections import (
        ResumeParsedSections,
        ParsedResumeSections,
        WorkExperienceItem,
        EducationItem,
    )
    from app.models.domain.dynamic_blueprint import (
        EvaluationQuestionsBlueprint,
        BackgroundClassificationBlueprint,
        AscendingAssessmentBlueprint,
        MandatoryDealbreakerBlueprint,
    )
    from app.models.domain.candidate_decision import (
        CandidateVerdict,
        GateResult,
        ScoreBreakdown,
    )

    assert JobRequisition is not None
    assert ParsedResume is not None
    assert CandidateEvaluation is not None
    assert ResumeParsedSections is not None
    assert ParsedResumeSections is not None
    assert WorkExperienceItem is not None
    assert EducationItem is not None
    assert EvaluationQuestionsBlueprint is not None
    assert BackgroundClassificationBlueprint is not None
    assert AscendingAssessmentBlueprint is not None
    assert MandatoryDealbreakerBlueprint is not None
    assert CandidateVerdict is not None
    assert GateResult is not None
    assert ScoreBreakdown is not None

    # 4. Schemas
    from app.schemas.recruitment import (
        JobAnalyzeRequest,
        JobAnalyzeResponse,
        JobQuestionsUpdateRequest,
        JobQuestionsUpdateResponse,
        ResumeUploadBatchResponse,
        ResumeDetailResponse,
        JobEvaluationRequest,
        CandidateEvaluationItem,
        JobEvaluationSummaryResponse,
    )

    assert JobAnalyzeRequest is not None
    assert JobAnalyzeResponse is not None
    assert JobQuestionsUpdateRequest is not None
    assert JobQuestionsUpdateResponse is not None
    assert ResumeUploadBatchResponse is not None
    assert ResumeDetailResponse is not None
    assert JobEvaluationRequest is not None
    assert CandidateEvaluationItem is not None
    assert JobEvaluationSummaryResponse is not None

    # 5. Repositories
    from app.repositories.job_repository import JobRepository
    from app.repositories.resume_repository import ResumeRepository
    from app.repositories.evaluation_repository import EvaluationRepository

    assert JobRepository is not None
    assert ResumeRepository is not None
    assert EvaluationRepository is not None

    # 6. Services
    from app.services.recruitment_service import RecruitmentService, recruitment_service

    assert RecruitmentService is not None
    assert recruitment_service is not None

    # 7. Engines
    from app.engines.jev.client import JevClient, jev_client
    from app.engines.laya.client import LayaClient, laya_client
    from app.engines.evaluation.speculative_fanout import (
        SpeculativeEvaluator,
        speculative_evaluator,
    )

    assert JevClient is not None
    assert jev_client is not None
    assert LayaClient is not None
    assert laya_client is not None
    assert SpeculativeEvaluator is not None
    assert speculative_evaluator is not None


def test_v1_endpoints_live_call():
    """Verify live HTTP calls against the unified canonical v1 endpoints."""
    with TestClient(app) as client:
        # 1. Health check via /api/v1/health
        res_health = client.get("/api/v1/health")
        assert res_health.status_code == 200
        data_health = res_health.json()
        assert data_health["status"] == "healthy"
        assert data_health["service"] == "careerlens-enterprise"

        # 2. Analyze Job Requisition via /api/v1/jobs/analyze
        res_job = client.post(
            "/api/v1/jobs/analyze",
            json={
                "role_title": "Senior AI Infrastructure Engineer",
                "job_description": "We are seeking a Senior AI Infrastructure Engineer with 5+ years of experience in Python, FastAPI, Docker, and PostgreSQL. Must have Kubernetes expertise.",
            },
        )
        assert res_job.status_code == 200
        data_job = res_job.json()
        assert "job_id" in data_job
        assert data_job["role_title"] == "Senior AI Infrastructure Engineer"
        assert len(data_job["questions"]) > 0

        job_id = data_job["job_id"]

        # 3. Retrieve Requisition via GET /api/v1/jobs/{job_id}
        res_get_job = client.get(f"/api/v1/jobs/{job_id}")
        assert res_get_job.status_code == 200
        assert res_get_job.json()["job_id"] == job_id

        # 4. Upload Resume via POST /api/v1/resumes/upload
        dummy_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        res_upload = client.post(
            "/api/v1/resumes/upload",
            files=[("files", ("candidate_infra.pdf", io.BytesIO(dummy_pdf), "application/pdf"))],
        )
        assert res_upload.status_code in (200, 202)
        data_upload = res_upload.json()
        assert data_upload["total_uploaded"] == 1
        assert len(data_upload["resumes"]) == 1
        resume_id = data_upload["resumes"][0]["resume_id"]

        # 5. Retrieve Parsed Resume via GET /api/v1/resumes/{resume_id}
        res_resume = client.get(f"/api/v1/resumes/{resume_id}")
        assert res_resume.status_code == 200
        data_resume = res_resume.json()
        assert data_resume["resume_id"] == resume_id
        assert data_resume["filename"] == "candidate_infra.pdf"
