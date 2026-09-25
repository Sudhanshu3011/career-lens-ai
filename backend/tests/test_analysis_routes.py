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
    assert data["pipeline"] == "deterministic-calibrated-laya"


def test_candidate_quick_apply_endpoints_removed():
    # Candidate endpoints should no longer exist in enterprise screener
    res1 = client.post("/api/v1/quick-apply", json={})
    assert res1.status_code in (404, 405)

    res2 = client.post("/api/v1/should-i-apply", json={})
    assert res2.status_code in (404, 405)
