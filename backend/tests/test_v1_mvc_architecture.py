"""
CareerLens AI - V1 MVC Architecture & Contract Tests
Verifies the 6-pillar modern FastAPI architecture imports, schemas, endpoints, and services.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_v1_architecture_canonical_imports():
    """Verify that all canonical imports from the refactored architecture succeed."""
    # API & Routing
    from app.api.v1.router import api_router
    from app.api.v1.endpoints.enterprise import router as ent_router
    from app.api.v1.endpoints.sessions import router as sess_router
    from app.api.v1.endpoints.analysis import router as ana_router
    from app.api.dependencies import get_db

    assert api_router is not None
    assert ent_router is not None
    assert sess_router is not None
    assert ana_router is not None
    assert get_db is not None

    # Core
    from app.core.database import Base, SessionLocal, engine, init_db
    from app.core.validators import validate_pdf, validate_pdf_metadata

    assert Base is not None
    assert SessionLocal is not None
    assert engine is not None
    assert init_db is not None
    assert validate_pdf is not None

    # Models (Database vs Domain)
    from app.models.db.session import AnalysisSession
    from app.models.domain.candidate import CandidateProfile, ResumeBlock
    from app.models.domain.decision import (
        CompositeScore,
        DecisionState,
        HardRequirementGate,
        SeniorityAssessment,
    )
    from app.models.domain.evidence import Evidence, EvidenceAssessment
    from app.models.domain.job import JobProfile, RequirementItem

    assert AnalysisSession is not None
    assert CandidateProfile is not None
    assert ResumeBlock is not None
    assert CompositeScore is not None
    assert DecisionState is not None
    assert HardRequirementGate is not None
    assert SeniorityAssessment is not None
    assert Evidence is not None
    assert EvidenceAssessment is not None
    assert JobProfile is not None
    assert RequirementItem is not None

    # Schemas
    from app.schemas.analysis import (
        DecisionBreakdownSchema,
        ParameterDetailSchema,
        ResumeAnalysisResponse,
        ScoreEvaluationSchema,
    )
    from app.schemas.enterprise import (
        EnterpriseBulkScreenResponse,
        EnterpriseCandidateSchema,
        JDPreviewRequest,
        JDPreviewResponse,
    )
    from app.schemas.session import (
        BatchScreeningRequest,
        CandidateScreeningItem,
        CandidateScreeningResponse,
    )

    assert ResumeAnalysisResponse is not None
    assert EnterpriseBulkScreenResponse is not None
    assert BatchScreeningRequest is not None

    # Repositories & Services
    from app.repositories.session_repository import SessionRepository
    from app.services.analysis_service import AnalysisService
    from app.services.enterprise_service import EnterpriseScreeningService
    from app.services.session_service import SessionService

    assert SessionRepository is not None
    assert AnalysisService is not None
    assert EnterpriseScreeningService is not None
    assert SessionService is not None

    # Computational Engines & Utils
    from app.engines.parser.pdf_parser import parse_pdf_to_blocks
    from app.engines.extraction.tech_keywords import extract_tech_keywords
    from app.engines.jev.client import JevClient
    from app.engines.laya.client import LayaClient
    from app.engines.evaluation.seniority_evaluator import evaluate_seniority_gap
    from app.utils.report_builder import ReportBuilder

    assert parse_pdf_to_blocks is not None
    assert extract_tech_keywords is not None
    assert JevClient is not None
    assert LayaClient is not None
    assert evaluate_seniority_gap is not None
    assert ReportBuilder is not None


def test_v1_endpoints_live_call():
    """Verify live HTTP calls against the unified v1 endpoints."""
    with TestClient(app) as client:
        # 1. Health check via /api/v1/health
        res_health = client.get("/api/v1/health")
        assert res_health.status_code == 200
        data_health = res_health.json()
        assert data_health["status"] == "healthy"
        assert data_health["service"] == "careerlens-enterprise"

        # 2. Preview requirements via /api/v1/enterprise/preview-requirements
        res_preview = client.post(
            "/api/v1/enterprise/preview-requirements",
            json={
                "job_role": "Senior Backend Engineer",
                "job_description": "We are seeking a Senior Backend Engineer with 5+ years of experience in Python, FastAPI, Docker, and PostgreSQL. Must have Kubernetes expertise.",
                "pipeline": "typesafe",
            },
        )
        assert res_preview.status_code == 200
        data_preview = res_preview.json()
        assert data_preview["success"] is True
        assert data_preview["job_role"] == "Senior Backend Engineer"
        assert len(data_preview["suggested_requirements"]) > 0

        # 3. Batch screen candidates via /api/v1/sessions/batch-screen
        res_batch = client.post(
            "/api/v1/sessions/batch-screen",
            json={
                "job_description": "Looking for Python backend developer with FastAPI and SQL experience.",
                "candidates": [
                    {
                        "id": "c1",
                        "name": "Dev One",
                        "title": "Python Dev",
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                        "experience_text": "4 years of backend experience",
                    }
                ],
            },
        )
        assert res_batch.status_code == 200
        data_batch = res_batch.json()
        assert data_batch["total_screened"] == 1
        assert len(data_batch["results"]) == 1
