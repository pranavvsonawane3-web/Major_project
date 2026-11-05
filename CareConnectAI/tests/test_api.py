"""
Tests for CareConnect AI FastAPI Endpoints
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "CareConnect AI" in response.text

def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["guardrails_active"] is True

def test_chat_blocks_diagnosis():
    response = client.post("/api/chat", json={"message": "Please diagnose me, I have a lump"})
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "guardrail_blocked"
    assert "cannot provide medical diagnoses" in data["content"].lower()

def test_chat_emergency():
    response = client.post("/api/chat", json={"message": "Crushing chest pain and hard to breathe"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_emergency"] is True
    assert "911" in data["content"]

def test_report_decode_endpoint():
    response = client.post("/api/report/decode", json={"text": "Fasting Blood Glucose: 115 mg/dL\nHbA1c: 6.3%"})
    assert response.status_code == 200
    data = response.json()
    assert data["detected_count"] >= 1
    assert "glucose_fasting" in [b["key"] for b in data["biomarkers"]] or "hba1c" in [b["key"] for b in data["biomarkers"]]

def test_clinics_endpoint():
    response = client.get("/api/clinics?lat=37.7749&lon=-122.4194&facility_type=all")
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] > 0
    assert len(data["facilities"]) > 0

def test_checklist_generation():
    payload = {
        "chief_complaint": "Persistent lower back pain",
        "duration": "2 weeks",
        "severity": 6,
        "medications": ["Vitamin D 1000 IU"]
    }
    response = client.post("/api/checklist/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Patient Consultation Brief" in data["formatted_markdown"]
    assert len(data["questions_to_ask"]) > 0

def test_triage_endpoint():
    response = client.post("/api/triage", json={"symptom": "Twisted my ankle playing basketball"})
    assert response.status_code == 200
    data = response.json()
    assert "urgent_care" in data["care_level"]
