import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aggregation import aggregate_predictions

def test_aggregation_empty():
    res = aggregate_predictions([])
    assert res["verdict"] == "INSUFFICIENT"
    assert res["counts"]["papers"] == 0

def test_aggregation_supported():
    predictions = [
        {"doc_id": "1", "prediction": "SUPPORT", "confidence": 0.9, "relevance_score": 0.8},
        {"doc_id": "2", "prediction": "SUPPORT", "confidence": 0.85, "relevance_score": 0.75},
        {"doc_id": "3", "prediction": "NEUTRAL", "confidence": 0.6, "relevance_score": 0.4},
    ]
    res = aggregate_predictions(predictions)
    assert res["verdict"] == "SUPPORTED"
    assert res["counts"]["support"] == 2
    assert res["counts"]["papers"] == 3
    assert res["strength"] in ["STRONG", "MODERATE"]

def test_aggregation_contradicted():
    predictions = [
        {"doc_id": "1", "prediction": "CONTRADICT", "confidence": 0.9, "relevance_score": 0.8},
        {"doc_id": "2", "prediction": "CONTRADICT", "confidence": 0.85, "relevance_score": 0.75},
        {"doc_id": "3", "prediction": "NEUTRAL", "confidence": 0.6, "relevance_score": 0.4},
    ]
    res = aggregate_predictions(predictions)
    assert res["verdict"] == "CONTRADICTED"
    assert res["counts"]["contradict"] == 2
    assert res["counts"]["papers"] == 3

def test_aggregation_mixed():
    predictions = [
        {"doc_id": "1", "prediction": "SUPPORT", "confidence": 0.8, "relevance_score": 0.8},
        {"doc_id": "2", "prediction": "CONTRADICT", "confidence": 0.8, "relevance_score": 0.8},
    ]
    res = aggregate_predictions(predictions)
    assert res["verdict"] == "MIXED"
    assert res["counts"]["support"] == 1
    assert res["counts"]["contradict"] == 1
