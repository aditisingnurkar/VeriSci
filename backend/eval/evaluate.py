import sys
import os
import json
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from retrieval.retrieve import retrieve_evidence, load_index
from ml.inference import classify_evidence, classifier
from aggregation import aggregate_predictions

def main():
    print("Loading index...")
    load_index()
    print("Loading classifier...")
    classifier.load()

    dev_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "claims_dev.jsonl")
    
    y_true = []
    y_pred = []
    errors = []

    print(f"Evaluating on {dev_file}")
    with open(dev_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in tqdm(lines, desc="Evaluating Claims"):
        data = json.loads(line)
        claim = data['claim']
        evidence = data['evidence']
        
        if not evidence:
            true_label = "INSUFFICIENT"
        else:
            # SciFact has one consistent label per claim
            first_doc = list(evidence.keys())[0]
            label = evidence[first_doc][0]['label']
            true_label = "SUPPORTED" if label == "SUPPORT" else "CONTRADICTED"
            
        retrieved = retrieve_evidence(claim, top_k=5)
        if not retrieved:
            pred_label = "INSUFFICIENT"
        else:
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
            pred_label = agg_result["verdict"]
            
        y_true.append(true_label)
        y_pred.append(pred_label)
        
        if true_label != pred_label:
            if len(errors) < 10:
                errors.append({
                    "claim": claim,
                    "true": true_label,
                    "pred": pred_label,
                    "retrieved_count": len(retrieved)
                })

    print("\n--- Full Pipeline Evaluation (SciFact Dev) ---")
    print(classification_report(y_true, y_pred, zero_division=0))
    print("Confusion Matrix:")
    labels = sorted(list(set(y_true + y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print(labels)
    print(cm)
    
    print("\nExample Errors:")
    for err in errors:
        print(f"Claim: {err['claim']}\n  True: {err['true']} | Pred: {err['pred']} | Retrieved: {err['retrieved_count']}")

if __name__ == "__main__":
    main()
