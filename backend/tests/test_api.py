import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app, verification_cache

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_retrieve():
    response = client.post("/api/retrieve", json={"claim": "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert "evidence" in data
    assert len(data["evidence"]) > 0
    assert "title" in data["evidence"][0]
    assert "evidence_text" in data["evidence"][0]

def test_retrieve_out_of_scope():
    response = client.post("/api/retrieve", json={"claim": "The moon is made of cheddar cheese and pasta.", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["evidence"] == []
    assert data.get("out_of_scope") is True

def test_verify_supported():
    response = client.post("/api/verify", json={"claim": "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.", "top_k": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["SUPPORTED", "CONTRADICTED", "MIXED", "INSUFFICIENT"]
    assert "verification_id" in data
    assert "counts" in data
    assert data["counts"]["papers"] >= 1
    assert "evidence" in data
    assert len(data["evidence"]) >= 1
    assert data["evidence"][0]["prediction"] in ["SUPPORT", "CONTRADICT", "NEUTRAL"]
    assert "confidence" in data["evidence"][0]

def test_verify_out_of_scope():
    response = client.post("/api/verify", json={"claim": "The moon is made of cheese and pasta.", "top_k": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "INSUFFICIENT"
    assert data["reason_code"] == "OUT_OF_SCOPE"
    assert len(data["evidence"]) == 0

def test_classify():
    response = client.post("/api/classify", json={
        "claim": "Mice lacking c-rel are protected against encephalomyelitis.",
        "evidence": ["Mice lacking c-rel were found to be resistant and protected against developing autoimmune encephalomyelitis."]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["prediction"] in ["SUPPORT", "CONTRADICT", "NEUTRAL"]
    assert "confidence" in data[0]

def test_explain_and_chat_mock():
    # Set mock provider for testing LLM
    os.environ["LLM_PROVIDER"] = "mock"
    
    # 1. Verify a claim to generate verification_id
    res_verify = client.post("/api/verify", json={"claim": "Mice lacking c-rel are protected against encephalomyelitis.", "top_k": 3})
    data_verify = res_verify.json()
    v_id = data_verify["verification_id"]
    
    # 2. Call explain
    res_explain = client.post("/api/explain", json={"verification_id": v_id})
    assert res_explain.status_code == 200
    data_explain = res_explain.json()
    assert "explanation" in data_explain
    assert "citations" in data_explain
    
    # 3. Call chat
    res_chat = client.post("/api/chat", json={
        "verification_id": v_id,
        "message": "What does the study show?",
        "history": []
    })
    assert res_chat.status_code == 200
    data_chat = res_chat.json()
    assert "answer" in data_chat
    assert "citations" in data_chat
