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
        
    if len(retrieved) > 0 and retrieved[0].get("out_of_scope"):
        print("  Verdict: INSUFFICIENT (Out of scope - non-biomedical claim)")
        return
        
    evidence_texts = [ev["evidence_text"] for ev in retrieved]
    ml_results = classify_evidence(claim, evidence_texts)
    
    predictions = []
    for ev, ml in zip(retrieved, ml_results):
        predictions.append({
            "doc_id": ev.get("doc_id", ""),
            "prediction": ml["prediction"],
            "confidence": ml["confidence"],
            "relevance_score": ev["relevance_score"]
        })
        
    agg_result = aggregate_predictions(predictions)
    print(f"  Verdict: {agg_result['verdict']} (Strength: {agg_result['strength']}, Score: {agg_result['score']:.4f})")
    print(f"  Reason: {agg_result['reason']}")
    print(f"  Evidence Counts: {agg_result['counts']}")
    print("  Retrieved Studies:")
    for idx, (ev, ml) in enumerate(zip(retrieved, ml_results)):
        print(f"    [{idx+1}] ({ev.get('source', 'SciFact')}) {ev.get('title')[:70]}...")
        print(f"        Passage: \"{ev.get('evidence_text')[:90]}...\"")
        print(f"        ML Prediction: {ml['prediction']} ({ml['confidence']*100:.1f}% conf)")
    
def main():
    if "--pubmed" in sys.argv:
        os.environ["ENABLE_PUBMED"] = "true"
        
    pubmed_active = os.environ.get("ENABLE_PUBMED", "false").lower() == "true"
    print(f"Loading index and models... (PubMed Integration: {'ENABLED' if pubmed_active else 'DISABLED'})")
    load_index()
    classifier.load()
    
    claims = [
        "Vaccines cause infertility.",
        "Vaccines do not cause infertility.",
        "MMR vaccine causes autism.",
        "Mice lacking c-rel are protected against experimental autoimmune encephalomyelitis.",
        "The moon is made of cheese and pasta."
    ]
    
    for claim in claims:
        check_claim(claim)

if __name__ == "__main__":
    main()
