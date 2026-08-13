from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_model_info_has_no_local_weights():
    r = client.get("/api/ai/model-info")
    assert r.status_code == 200
    data = r.json()
    assert data["local_model_weights"] is False
    assert data["model_version"] == "hf-llama-3.1-8b-triage-v1"


def test_critical_safety_rule_never_depends_on_llm():
    r = client.post("/api/ai/analyse", json={
        "title": "Exposed electrical wiring outside science laboratory",
        "description": "Several exposed electrical wires are hanging next to the entrance and students are walking close to them.",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["priority"]["label"] == "CRITICAL"
    assert data["decision_source"] == "SAFETY_RULE"


def test_normal_it_not_critical():
    data = client.post("/api/ai/analyse", json={"title":"Library Wi-Fi problem","description":"The Wi-Fi in Library Level 2 disconnects every few minutes."}).json()
    assert data["category"]["label"] == "IT"
    assert data["priority"]["label"] != "CRITICAL"


def test_positive_feedback_supported():
    data = client.post("/api/ai/analyse", json={"title":"Helpful library service","description":"Thank you, the library service is working well and staff were helpful."}).json()
    assert data["sentiment"]["label"] == "POSITIVE"


def test_empty_input_rejected():
    assert client.post("/api/ai/analyse", json={"title":"","description":""}).status_code == 422


def test_ambiguous_feedback_marks_review():
    data = client.post("/api/ai/analyse", json={"title":"Something changed","description":"The situation is different today and I am unsure where it belongs."}).json()
    assert data["needs_review"] is True
