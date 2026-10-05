# Phase 5: End-to-End Evaluation & Final UI

## Final System Metrics
We evaluated the full end-to-end pipeline (Document + Sentence Retrieval -> Claim Verification ML -> Verdict Aggregation) on the SciFact dev claims dataset (`data/claims_dev.jsonl`).

**End-to-End Evaluation Results (SciFact Dev):**
- **Macro-F1 Score**: 0.31
- **Accuracy**: 0.45

*Confusion Matrix:*
```text
['CONTRADICTED', 'INSUFFICIENT', 'MIXED', 'SUPPORTED']
[[13 22  1 28]
 [10 80  1 21]
 [ 0  0  0  0]
 [26 52  3 43]]
```

## Model Selection (Baseline vs. Transformer)
We tested a linear SVM trained on TF-IDF + overlap + negation features (with hard-negative mining) against a zero-shot NLI transformer (`cross-encoder/nli-distilroberta-base`).

**Result:** The **Baseline Linear SVM** won.
- **Baseline Evidence Classifier Macro-F1**: 0.4167
- **Transformer Evidence Classifier Macro-F1**: 0.3654

The transformer struggled heavily with the SciFact domain (e.g., failing to recognize scientific entailment vs contradiction correctly without fine-tuning), whereas our baseline explicitly used overlap and negation heuristics that proved more robust on this specific validation set. We shipped the baseline.

## Final UI State
The frontend was completely overhauled to surface the verdict first and clearly present the supporting data.
- **Hero Verdict Block**: A large, color-coded block (Green for Supported, Red for Contradicted, Amber for Mixed/Insufficient) presenting the final plain-language verdict and strength.
- **Evidence Breakdown**: A clear count of how many papers/passages were analyzed and their respective ML assessments (Support/Contradict/Neutral).
- **Evidence Cards**: Clean, modern cards that show the paper title, the specific extracted snippet, the relevance score, and the localized ML assessment for that specific piece of evidence.
- **Mock Data Removed**: The application now exclusively uses live data from the FastAPI backend.
