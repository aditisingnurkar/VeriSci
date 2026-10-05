import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from retrieval.retrieve import retrieve_evidence, load_index
from ml.inference import classify_evidence, classifier
from aggregation import aggregate_predictions

def check_claim(claim):
    print(f"\nClaim: {claim}")
    retrieved = retrieve_evidence(claim, top_k=5)
    if not retrieved:
        print("  Verdict: INSUFFICIENT (No evidence)")
        return
        
    evidence_texts = [ev["evidence_text"] for ev in retrieved]
    ml_results = classify_evidence(claim, evidence_texts)
    
    predictions = []
    for ev, ml in zip(retrieved, ml_results):
        predictions.append({
            "doc_id": ev["doc_id"],
            "prediction": ml["prediction"],
            "confidence": ml["confidence"],
            "relevance_score": ev["relevance_score"]
        })
        
    agg_result = aggregate_predictions(predictions)
    print(f"  Verdict: {agg_result['verdict']} (Strength: {agg_result['strength']}, Score: {agg_result['score']:.4f})")
    print(f"  Reason: {agg_result['reason']}")
    print(f"  Evidence Counts: {agg_result['counts']}")
    
def main():
    print("Loading index and models...")
    load_index()
    classifier.load()
    
    claims = [
        "Vaccines cause infertility.",
        "Vaccines do not cause infertility.",
        "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.",
        "The moon is made of cheese and pasta."
    ]
    
    for claim in claims:
        check_claim(claim)

if __name__ == "__main__":
    main()
