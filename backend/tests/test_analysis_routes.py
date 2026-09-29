import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "careerlens-enterprise"
    assert data["pipeline"] == "universal-speculative-fanout"


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "CareerLens AI API"
    assert data["status"] == "online"


def test_analysis_router_and_legacy_routes_import():
    from app.api.v1.endpoints.analysis import router as analysis_router
    from app.api.v1.router import api_router

    assert analysis_router is not None
    assert api_router is not None


def test_pdf_validator_scenarios():
    import io
    from app.core.validators import validate_pdf
    from fastapi import UploadFile, HTTPException

    valid_file = UploadFile(
        file=io.BytesIO(b"%PDF-1.4 sample content"),
        filename="resume.pdf",
        headers={"content-type": "application/pdf"},
    )
    validate_pdf(valid_file, b"%PDF-1.4 sample content")

    invalid_ext = UploadFile(
        file=io.BytesIO(b"%PDF-1.4 content"),
        filename="resume.docx",
        headers={"content-type": "application/pdf"},
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_pdf(invalid_ext, b"%PDF-1.4 content")
    assert exc_info.value.status_code == 400

    invalid_magic = UploadFile(
        file=io.BytesIO(b"not a real pdf"),
        filename="resume.pdf",
        headers={"content-type": "application/pdf"},
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_pdf(invalid_magic, b"not a real pdf")
    assert exc_info.value.status_code == 400
