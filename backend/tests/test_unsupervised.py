import os
import pytest
from fastapi.testclient import TestClient

from ml.unsupervised_model import get_unsupervised_model
from aggregation import aggregate_predictions
from main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def model():
    m = get_unsupervised_model()
    assert m.load(), "Failed to load unsupervised model artifacts"
    return m

def test_unsupervised_model_artifacts_loaded(model):
    assert model.kmeans is not None
    assert model.cluster_mapping is not None
    assert len(model.cluster_mapping) == 3
    for cid in ["0", "1", "2"]:
        assert cid in model.cluster_mapping
        assert model.cluster_mapping[cid] in ["SUPPORT", "CONTRADICT", "NEUTRAL"]

def test_predict_single_and_batch(model):
    claim = "Vitamin D reduces viral respiratory infections."
    evidence_list = [
        "Multiple randomized trials found vitamin D supplementation significantly reduced respiratory infection risk.",
        "A large double-blind trial demonstrated no significant difference in infection rates between vitamin D and placebo groups.",
        "Patients were monitored over a 12-month period for diverse biomarkers."
    ]

    preds = model.predict_batch(claim, evidence_list)
    assert len(preds) == len(evidence_list)

    for p in preds:
        assert p["prediction"] in ["SUPPORT", "CONTRADICT", "NEUTRAL"]
        assert 0.0 <= p["confidence"] <= 1.0
        assert p["cluster_id"] in [0, 1, 2]
        assert p["centroid_distance"] >= 0.0
        assert 0.0 < p["cluster_affinity"] <= 1.0
        assert len(p["all_distances"]) == 3
        assert p["is_unsupervised"] is True
        assert p["stance_source"] == "unsupervised_cluster_mapping"
        # Validate geometric affinity formula
        expected_affinity = 1.0 / (1.0 + p["centroid_distance"])
        assert abs(p["cluster_affinity"] - expected_affinity) < 1e-3

def test_aggregation_with_unsupervised_diagnostics():
    predictions = [
        {
            "prediction": "SUPPORT",
            "confidence": 0.85,
            "cluster_id": 1,
            "centroid_distance": 0.45,
            "cluster_affinity": 0.69,
            "relevance_score": 0.90,
            "evidence_text": "Evidence 1 affirms the finding."
        },
        {
            "prediction": "SUPPORT",
            "confidence": 0.80,
            "cluster_id": 1,
            "centroid_distance": 0.52,
            "cluster_affinity": 0.66,
            "relevance_score": 0.85,
            "evidence_text": "Evidence 2 corroborates the effect."
        },
        {
            "prediction": "NEUTRAL",
            "confidence": 0.60,
            "cluster_id": 0,
            "centroid_distance": 0.70,
            "cluster_affinity": 0.58,
            "relevance_score": 0.40,
            "evidence_text": "Evidence 3 is unrelated."
        }
    ]

    agg = aggregate_predictions(predictions)
    assert agg["verdict"] == "SUPPORTED"
    assert agg["counts"]["support"] == 2
    assert agg["counts"]["neutral"] == 1
    assert agg["dominant_cluster"] == 1
    assert "1" in agg["cluster_weights"]
    assert "Unsupervised K-Means" in agg["methodology"]

def test_comparison_endpoint(client):
    res = client.get("/api/comparison")
    assert res.status_code == 200
    data = res.json()
    assert "unsupervised_model" in data
    assert "supervised_baseline" in data
    assert "comparison_samples" in data
    
    unsup = data["unsupervised_model"]
    assert "raw_clustering_metrics" in unsup
    assert "silhouette_score" in unsup["raw_clustering_metrics"]
    assert "adjusted_rand_index" in unsup["raw_clustering_metrics"]
    assert "normalized_mutual_info" in unsup["raw_clustering_metrics"]
    assert "contingency_table" in unsup
    assert "mapped_classification_metrics" in unsup

    sup = data["supervised_baseline"]
    assert "classification_metrics" in sup
    assert sup["classification_metrics"]["accuracy"] > unsup["mapped_classification_metrics"]["accuracy"]

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "unsupervised" in data.get("model", "").lower()
