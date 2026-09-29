from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_demo_finding_exists():
    r = client.get("/api/findings")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_review():
    r = client.post("/api/findings/1/review", json={
        "decision": "UNCERTAIN",
        "comment": "Demo review",
        "analyst": "test_analyst"
    })
    assert r.status_code == 200
    assert r.json()["finding"]["review_status"] == "UNCERTAIN"
