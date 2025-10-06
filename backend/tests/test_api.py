import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_list_scenarios():
    resp = client.get("/api/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(s["name"] == "Hiring Bias Demo" for s in data)

def test_simulate():
    # Get demo scenario id
    scenarios = client.get("/api/scenarios").json()
    demo = next(s for s in scenarios if s["name"] == "Hiring Bias Demo")
    payload = {
        "scenario_id": demo["id"],
        "frameworks": ["utilitarian", "fairness", "rule_based"],
        "params": {"top_k": 2, "weights": {"experience": 0.5, "test_score": 0.5}}
    }
    resp = client.post("/api/simulate", json=payload)
    assert resp.status_code == 200
    run = resp.json()
    assert "results" in run and len(run["results"]) >= 3