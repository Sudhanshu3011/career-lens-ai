"""
CareerLens AI - Session Routes & Service Integration Tests
Verifies HTTP endpoints for creating, retrieving, stepping through, and batch screening sessions.
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db


@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database schema is created for test runs."""
    init_db()


def test_session_lifecycle_and_steps():
    with TestClient(app) as client:
        # 1. Invalid PDF returns 400 Bad Request
        corrupt_pdf = b"%PDF-1.4\ncorrupted_data_without_root"
        files_bad = {
            "file": ("corrupt.pdf", io.BytesIO(corrupt_pdf), "application/pdf")
        }
        data = {
            "job_description": "Senior Python developer with 5+ years experience with FastAPI, Docker, and PostgreSQL."
        }
        res_bad = client.post("/api/v1/sessions", files=files_bad, data=data)
        assert res_bad.status_code == 400
        assert "extract text" in res_bad.json()["detail"].lower()

        # 2. Valid PDF creates session
        valid_pdf_content = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
            b"4 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n"
            b"(John Doe\\nSenior Python Engineer with 6 years experience in FastAPI, Docker, and PostgreSQL.) Tj\n"
            b"ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n"
            b"0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n"
            b"0000000216 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n470\n%%EOF"
        )
        files = {
            "file": ("john_doe.pdf", io.BytesIO(valid_pdf_content), "application/pdf")
        }
        res_create = client.post("/api/v1/sessions", files=files, data=data)
        assert res_create.status_code == 201
        session_id = res_create.json()["session_id"]
        assert session_id is not None

        # 3. Step 1: Parse
        r1 = client.post(f"/api/v1/sessions/{session_id}/steps/parse")
        assert r1.status_code == 200
        assert r1.json()["step"] == 1

        # 4. Step 2: Skills
        r2 = client.post(f"/api/v1/sessions/{session_id}/steps/skills")
        assert r2.status_code == 200
        assert r2.json()["step"] == 2

        # 5. Step 3: Decision
        r3 = client.post(f"/api/v1/sessions/{session_id}/steps/decision")
        assert r3.status_code == 200
        assert r3.json()["step"] == 3

        # 6. Step 4: Feedback
        r4 = client.post(f"/api/v1/sessions/{session_id}/steps/feedback")
        assert r4.status_code == 200
        assert r4.json()["step"] == 4

        # 7. Step 5: Jobs
        r5 = client.post(f"/api/v1/sessions/{session_id}/steps/jobs")
        assert r5.status_code == 200
        assert r5.json()["step"] == 5

        # 8. Retrieve Session Details
        r_get = client.get(f"/api/v1/sessions/{session_id}")
        assert r_get.status_code == 200
        assert r_get.json()["status"] == "completed"

        # 9. List Sessions
        r_list = client.get("/api/v1/sessions")
        assert r_list.status_code == 200
        assert len(r_list.json()) >= 1


def test_batch_screen_candidates_endpoint():
    with TestClient(app) as client:
        payload = {
            "job_description": "Senior Backend Engineer with Python, FastAPI, and Docker skills.",
            "candidates": [
                {
                    "id": "c1",
                    "name": "Jane Smith",
                    "title": "Backend Dev",
                    "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                    "experience_text": "5 years building microservices",
                },
                {
                    "id": "c2",
                    "name": "Bob Jones",
                    "title": "Frontend Dev",
                    "skills": ["HTML", "CSS"],
                    "experience_text": "1 year frontend",
                },
            ],
        }
        res = client.post("/api/sessions/batch-screen", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_screened"] == 2
        assert len(data["results"]) == 2
        assert (
            data["results"][0]["decision"]["final_score"]
            >= data["results"][1]["decision"]["final_score"]
        )
