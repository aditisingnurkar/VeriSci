import os
import sys
import pickle
import pytest
import pandas as pd
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ml.unified_pipeline import UnifiedDatasetPipeline, normalize_label, normalize_text, LABEL_VOCABULARY
from ml.features import FeatureExtractor
from ml.inference import classify_evidence, classifier
from aggregation import aggregate_predictions
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def pipeline():
    return UnifiedDatasetPipeline()

def test_label_normalization():
    assert normalize_label("Supports", source="HealthVer") == "SUPPORT"
    assert normalize_label("Refutes", source="HealthVer") == "CONTRADICT"
    assert normalize_label("Neutral", source="HealthVer") == "NEUTRAL"
    assert normalize_label("ENTAILMENT", source="ManConCorpus") == "SUPPORT"
    assert normalize_label("CONTRADICTION", source="ManConCorpus") == "CONTRADICT"
    assert normalize_label("SUPPORT", source="SciFact") == "SUPPORT"
    assert normalize_label("REFUTES", source="SciFact") == "CONTRADICT"
    assert normalize_label("NOT ENOUGH INFO", source="SciFact") == "NEUTRAL"

    # Unsupported labels must raise an error
    with pytest.raises(ValueError):
        normalize_label("INVALID_UNKNOWN_LABEL", source="Test")

def test_text_normalization():
    raw = "  This   is a \n test \t claim with 10% NaCl.   "
    clean = normalize_text(raw)
    assert clean == "This is a test claim with 10% NaCl."

def test_schema_validation_and_required_fields(pipeline):
    required_cols = [
        "claim_id", "claim_text", "evidence_id", "evidence_text",
        "original_label", "normalized_label", "source_dataset",
        "source_document_id", "provenance", "split"
    ]
    # Check HealthVer
    hv_df = pipeline.load_healthver("dev")
    for col in required_cols:
        assert col in hv_df.columns, f"Missing required column {col} in HealthVer"
    assert len(hv_df) > 0
    assert set(hv_df["normalized_label"].unique()).issubset(LABEL_VOCABULARY)

    # Check ManConCorpus
    mc_df = pipeline.load_mancon("dev")
    for col in required_cols:
        assert col in mc_df.columns, f"Missing required column {col} in ManConCorpus"
    assert len(mc_df) > 0
    assert set(mc_df["normalized_label"].unique()).issubset(LABEL_VOCABULARY)

    # Check SciFact
    sf_df = pipeline.load_scifact("dev")
    for col in required_cols:
        assert col in sf_df.columns, f"Missing required column {col} in SciFact"
    assert len(sf_df) > 0
    assert set(sf_df["normalized_label"].unique()).issubset(LABEL_VOCABULARY)

def test_data_split_isolation_and_no_leakage(pipeline):
    hv_tr = pipeline.load_healthver("train")
    hv_dev = pipeline.load_healthver("dev")
    exact_overlap, claim_overlap = pipeline.verify_leakage(hv_tr, hv_dev)
    assert exact_overlap == 0, "Data leakage detected: train and dev share exact pairs in HealthVer!"

    mc_tr = pipeline.load_mancon("train")
    mc_dev = pipeline.load_mancon("dev")
    mc_exact, _ = pipeline.verify_leakage(mc_tr, mc_dev)
    assert mc_exact == 0, "Data leakage detected: train and dev share exact pairs in ManConCorpus!"

def test_model_serialization_and_reloading():
    models_dir = os.path.join(BASE_DIR, "models")
    model_path = os.path.join(models_dir, "evidence_classifier.pkl")
    extractor_path = os.path.join(models_dir, "feature_extractor.pkl")
    metadata_path = os.path.join(models_dir, "model_metadata.json")

    assert os.path.exists(model_path), "Model artifact evidence_classifier.pkl is missing"
    assert os.path.exists(extractor_path), "Feature extractor artifact feature_extractor.pkl is missing"
    assert os.path.exists(metadata_path), "Metadata file model_metadata.json is missing"

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(extractor_path, "rb") as f:
        extractor = pickle.load(f)

    assert hasattr(model, "predict"), "Loaded model has no predict method"
    assert hasattr(extractor, "transform"), "Loaded extractor has no transform method"

def test_inference_classification_labels():
    claim = "L-Arginine supplementation reduces blood pressure in pre-eclampsia."
    evidence = [
        "Supplementation with L-arginine significantly reduced diastolic blood pressure.",
        "L-arginine did not reduce blood pressure in women with pre-eclampsia.",
        "A total of 45 patients were enrolled in the medical trial."
    ]
    results = classify_evidence(claim, evidence)
    assert len(results) == 3
    for res in results:
        assert "prediction" in res
        assert "confidence" in res
        assert res["prediction"] in LABEL_VOCABULARY
        assert 0.0 <= res["confidence"] <= 1.0

def test_verdict_aggregation_with_new_predictions():
    predictions = [
        {"doc_id": "1", "prediction": "SUPPORT", "confidence": 0.85, "relevance_score": 0.9},
        {"doc_id": "2", "prediction": "SUPPORT", "confidence": 0.80, "relevance_score": 0.85},
        {"doc_id": "3", "prediction": "NEUTRAL", "confidence": 0.70, "relevance_score": 0.5}
    ]
    verdict = aggregate_predictions(predictions)
    assert verdict["verdict"] == "SUPPORTED"
    assert verdict["strength"] in ["STRONG", "MODERATE", "WEAK"]
    assert verdict["counts"]["support"] == 2
    assert verdict["counts"]["neutral"] == 1

def test_api_verify_endpoint_compatibility():
    response = client.post("/api/verify", json={
        "claim": "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert data["verdict"] in ["SUPPORTED", "CONTRADICTED", "MIXED", "INSUFFICIENT"]
    assert "evidence" in data
    assert len(data["evidence"]) > 0
    assert data["evidence"][0]["prediction"] in LABEL_VOCABULARY

def test_api_classify_endpoint_compatibility():
    response = client.post("/api/classify", json={
        "claim": "COVID-19 vaccination prevents severe infection.",
        "evidence": ["Vaccines provided high effectiveness against severe COVID-19 hospitalisation."]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["prediction"] in LABEL_VOCABULARY
    assert data[0]["confidence"] > 0
