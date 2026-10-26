import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from ml.inference import classifier, classify_evidence
from aggregation import aggregate_predictions
from retrieval.spelling import check_claim_spelling, PROTECTED_TERMS

client = TestClient(app)

# ---------------------------------------------------------
# 1. NLI Input Ordering & Dynamic Label Mapping Tests
# ---------------------------------------------------------

def test_nli_input_order_and_label_mapping():
    """Verify that EvidenceClassifier loads dynamic label mapping and sets correct NLI convention."""
    classifier.load()
    assert classifier.model is not None
    assert classifier.extractor is not None
    assert hasattr(classifier, "label_map")
    assert "CONTRADICT" in classifier.label_map.values()
    assert "SUPPORT" in classifier.label_map.values()
    assert "NEUTRAL" in classifier.label_map.values()

def test_random_forest_artifact_and_feature_compatibility():
    """Verify that the deployed model is the three-dataset Random Forest with compatible feature extraction."""
    classifier.load()
    from sklearn.ensemble import RandomForestClassifier
    assert isinstance(classifier.model, RandomForestClassifier)
    assert classifier.model.n_features_in_ == 10022

    claim = "Metformin lowers blood glucose."
    evidence = ["Metformin significantly reduces fasting plasma glucose levels in type 2 diabetes."]
    preds = classifier.predict(claim, evidence)
    assert len(preds) == 1
    assert preds[0]["prediction"] in ["SUPPORT", "CONTRADICT", "NEUTRAL"]
    assert 0.0 <= preds[0]["confidence"] <= 1.0


# ---------------------------------------------------------
# 2. Negation & Directional Stance Semantic Tests
# ---------------------------------------------------------

def test_negated_vs_positive_claim_against_identical_evidence():
    """
    Test positive claim vs negated claim against the exact same evidence.
    Evidence refutes positive claim and entails negated claim.
    """
    evidence = [
        "Extensive epidemiological studies involving millions of children show that the MMR vaccine does not cause autism."
    ]
    positive_claim = "MMR vaccine causes autism."
    negated_claim = "MMR vaccine does not cause autism."

    pos_res = classifier.predict(positive_claim, evidence)
    neg_res = classifier.predict(negated_claim, evidence)

    assert pos_res[0]["prediction"] == "CONTRADICT", f"Expected CONTRADICT, got {pos_res[0]}"
    assert neg_res[0]["prediction"] == "SUPPORT", f"Expected SUPPORT, got {neg_res[0]}"

def test_direction_causality_distinctions():
    """
    Test scientifically meaningful directional distinctions (increase vs decrease)
    against identical evidence.
    """
    evidence = [
        "Statins significantly reduce low-density lipoprotein cholesterol levels in patients with hypercholesterolemia."
    ]
    claim_increase = "Statins increase LDL cholesterol."
    claim_decrease = "Statins decrease LDL cholesterol."

    inc_res = classifier.predict(claim_increase, evidence)
    dec_res = classifier.predict(claim_decrease, evidence)

    assert inc_res[0]["prediction"] == "CONTRADICT", f"Expected CONTRADICT, got {inc_res[0]}"
    assert dec_res[0]["prediction"] == "SUPPORT", f"Expected SUPPORT, got {dec_res[0]}"

def test_absence_of_evidence_is_neutral():
    """
    Verify that lack of evidence or unrelated trial details are classified as NEUTRAL,
    not falsely marked as CONTRADICT or SUPPORT.
    """
    evidence = [
        "The clinical trial enrolled 500 participants with mild hypertension and monitored blood pressure for 12 weeks."
    ]
    unrelated_claim = "The medication causes severe skin rash."

    res = classifier.predict(unrelated_claim, evidence)
    assert res[0]["prediction"] == "NEUTRAL", f"Expected NEUTRAL, got {res[0]}"


# ---------------------------------------------------------
# 3. Spelling Suggestion & Protected Term Tests
# ---------------------------------------------------------

def test_spelling_correction_common_typos():
    """Test that typos in biomedical words are accurately detected and suggested."""
    res1 = check_claim_spelling("Metfomin reduces blood suger in diabetic patients.")
    assert res1["has_suggestion"] is True
    assert "metformin" in res1["suggested_claim"].lower()
    assert "sugar" in res1["suggested_claim"].lower()

    res2 = check_claim_spelling("Vacinnes do not cause autism.")
    assert res2["has_suggestion"] is True
    assert "vaccines" in res2["suggested_claim"].lower()

def test_spelling_preserves_valid_biomedical_and_protected_terms():
    """Test that valid biomedical terms and meaning-critical negation/causal words are never altered."""
    res = check_claim_spelling("Autophagy promotes cellular homeostasis without increasing apoptotic cell death.")
    assert res["has_suggestion"] is False
    assert res["original_claim"] == res["suggested_claim"]

    for term in ["not", "no", "never", "without", "increase", "decrease", "cause", "prevent"]:
        assert term in PROTECTED_TERMS

def test_spellcheck_api_endpoint():
    """Test the POST /api/spellcheck endpoint contract."""
    response = client.post("/api/spellcheck", json={"claim": "Chlesterol levels elevate cardiac risk."})
    assert response.status_code == 200
    data = response.json()
    assert "has_suggestion" in data
    assert "original_claim" in data
    assert "suggested_claim" in data
    assert "corrections" in data
    assert data["has_suggestion"] is True
    assert "cholesterol" in data["suggested_claim"].lower()


# ---------------------------------------------------------
# 4. Aggregation Consistency Tests
# ---------------------------------------------------------

def test_aggregation_corroborating_papers_and_neutral_isolation():
    """
    Ensure neutral passages do not artificially inflate the strength of a verdict.
    2 supporting papers + 3 neutral papers should be MODERATE, not inflated to STRONG by neutral counts.
    """
    predictions = [
        {"doc_id": "P1", "prediction": "SUPPORT", "confidence": 0.85, "relevance_score": 0.8},
        {"doc_id": "P2", "prediction": "SUPPORT", "confidence": 0.80, "relevance_score": 0.75},
        {"doc_id": "P3", "prediction": "NEUTRAL", "confidence": 0.60, "relevance_score": 0.7},
        {"doc_id": "P4", "prediction": "NEUTRAL", "confidence": 0.60, "relevance_score": 0.7},
        {"doc_id": "P5", "prediction": "NEUTRAL", "confidence": 0.60, "relevance_score": 0.7},
    ]
    res = aggregate_predictions(predictions)
    assert res["verdict"] == "SUPPORTED"
    assert res["counts"]["support"] == 2
    assert res["counts"]["neutral"] == 3
    assert res["strength"] == "MODERATE"

def test_aggregation_multiple_passages_same_paper_deduplication():
    """
    Multiple passages from the exact same paper must take the max vote weight
    and not create duplicate independent paper votes.
    """
    predictions = [
        {"doc_id": "P1", "prediction": "SUPPORT", "confidence": 0.90, "relevance_score": 0.85},
        {"doc_id": "P1", "prediction": "SUPPORT", "confidence": 0.85, "relevance_score": 0.80},
        {"doc_id": "P1", "prediction": "SUPPORT", "confidence": 0.70, "relevance_score": 0.60},
    ]
    res = aggregate_predictions(predictions)
    assert res["verdict"] == "SUPPORTED"
    assert res["counts"]["papers"] == 1
    # 1 paper should be WEAK or MODERATE, never STRONG
    assert res["strength"] in ["WEAK", "MODERATE"]

def test_aggregation_conflicting_papers_mixed():
    """Equally weighted conflicting papers produce a MIXED verdict."""
    predictions = [
        {"doc_id": "P1", "prediction": "SUPPORT", "confidence": 0.85, "relevance_score": 0.8},
        {"doc_id": "P2", "prediction": "CONTRADICT", "confidence": 0.85, "relevance_score": 0.8},
    ]
    res = aggregate_predictions(predictions)
    assert res["verdict"] == "MIXED"
    assert res["counts"]["support"] == 1
    assert res["counts"]["contradict"] == 1


# ---------------------------------------------------------
# 5. End-to-End API Consistency & Claim Preservation
# ---------------------------------------------------------

def test_api_verify_preserves_original_claim_and_includes_spelling():
    """
    Test that POST /api/verify preserves the exact original claim text
    and attaches conservative spelling suggestions.
    """
    raw_claim = "Vacinnes do not cause autism in children."
    response = client.post("/api/verify", json={"claim": raw_claim, "top_k": 3})
    assert response.status_code == 200
    data = response.json()

    # Exact claim preserved
    assert data["claim"] == raw_claim
    assert "spelling_suggestion" in data
    assert data["spelling_suggestion"]["has_suggestion"] is True
    assert "vaccines" in data["spelling_suggestion"]["suggested_claim"].lower()
    assert data["verdict"] in ["SUPPORTED", "CONTRADICTED", "MIXED", "INSUFFICIENT"]
