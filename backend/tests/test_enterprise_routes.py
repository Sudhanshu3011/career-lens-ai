import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bulk_screen_empty_resumes():
    res = client.post(
        "/api/v1/enterprise/bulk-screen",
        data={
            "job_role": "Backend Engineer",
            "job_description": "We need a strong Python and FastAPI engineer with Docker.",
        },
    )
    assert res.status_code == 422  # missing resumes


def test_bulk_screen_with_multiple_resumes():
    # Use real AIML_resume.pdf or mock pdf bytes
    try:
        with open("AIML_resume.pdf", "rb") as f:
            pdf1 = f.read()
    except FileNotFoundError:
        pdf1 = b"%PDF-1.4 mock pdf data 1 " + b"0" * 300

    pdf2 = b"%PDF-1.4 mock pdf data 2 " + b"0" * 300
    pdf3 = b"%PDF-1.4 mock pdf data 3 " + b"0" * 300
    pdf4 = b"%PDF-1.4 mock pdf data 4 " + b"0" * 300

    files = [
        ("resumes", ("candidate_1.pdf", pdf1, "application/pdf")),
        ("resumes", ("candidate_2.pdf", pdf2, "application/pdf")),
        ("resumes", ("candidate_3.pdf", pdf3, "application/pdf")),
        ("resumes", ("candidate_4.pdf", pdf4, "application/pdf")),
    ]

    res = client.post(
        "/api/v1/enterprise/bulk-screen",
        files=files,
        data={
            "job_role": "AI / Machine Learning Engineer",
            "job_description": "We are seeking an AI / ML Engineer proficient in Python, PyTorch, Deep Learning, and FastAPI.",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_evaluated"] >= 1
    assert data["top_3_shortlisted"] == min(3, data["total_evaluated"])

    # Check candidate sorting and top 3 flagging
    candidates = data["candidates"]
    for i in range(len(candidates) - 1):
        assert candidates[i]["fit_score"] >= candidates[i + 1]["fit_score"]

    for cand in candidates:
        if cand["rank"] <= 3:
            assert cand["is_top_3"] is True
        else:
            assert cand["is_top_3"] is False


def test_bulk_screen_rejects_non_pdf_extension():
    files = [
        ("resumes", ("resume.docx", b"dummy word content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
    ]
    res = client.post(
        "/api/v1/enterprise/bulk-screen",
        files=files,
        data={
            "job_role": "Backend Engineer",
            "job_description": "We need a strong Python and FastAPI engineer with Docker.",
        },
    )
    assert res.status_code == 400
    assert "not a PDF" in res.json()["detail"]


def test_bulk_screen_rejects_invalid_mime_type():
    files = [
        ("resumes", ("resume.pdf", b"dummy content", "image/png")),
    ]
    res = client.post(
        "/api/v1/enterprise/bulk-screen",
        files=files,
        data={
            "job_role": "Backend Engineer",
            "job_description": "We need a strong Python and FastAPI engineer with Docker.",
        },
    )
    assert res.status_code == 400
    assert "invalid MIME type" in res.json()["detail"]
