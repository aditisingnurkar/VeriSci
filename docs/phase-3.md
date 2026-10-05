# Phase 3: Machine Learning Evidence Classifier

## Objective
The objective of Phase 3 is to build the genuine Machine Learning component of VeriSci. This component is responsible for classifying the relationship between a scientific claim and a piece of scientific evidence text as either `SUPPORT`, `CONTRADICT`, or `NEUTRAL`.

Unlike Phase 2, which focuses on information retrieval ("Which evidence is relevant?"), Phase 3 focuses on entailment ("Given this claim and this evidence, what is their relationship?"). This classification task takes both the claim and the retrieved evidence passage as input and provides a prediction with confidence scores.

## Exact ML Task
- **Input**: A scientific claim (string) and an evidence passage (string).
- **Task**: Multi-class classification (Predicting entailment relation).
- **Output**: A predicted label (`SUPPORT`, `CONTRADICT`, or `NEUTRAL`) and a calibrated confidence probability.

## Dataset Construction & Preparation
We used the official [SciFact](https://github.com/allenai/scifact) dataset and splits for training and evaluation.

To construct the labeled claim-evidence examples:
1. **SUPPORT/CONTRADICT**: We used the exact annotations provided in the SciFact `claims_train.jsonl` and `claims_dev.jsonl` files. SciFact annotates evidence at the sentence level. We extracted the specific evidence sentences that form rationales for claims and paired them with the claim along with their given label (`SUPPORT` or `CONTRADICT`).
2. **NEUTRAL**: Neutral examples were carefully constructed to avoid data leakage and excessive class imbalance. We sampled:
   - Sentences within evidence documents that were *not* part of the support or contradict rationales.
   - Sentences from documents that were cited but contained no evidence for or against the claim.

This approach aligns with the dataset's actual semantics, mapping perfectly to the sentence-level retrieval pipeline built in Phase 2.

### Train/Validation/Test Setup
- **Train Set**: Derived from `claims_train.jsonl` (~2,500 samples).
- **Dev/Validation Set**: Derived from `claims_dev.jsonl` (~900 samples).
- We maintain strict separation of training and evaluation data to ensure results remain reproducible and fair.

## Preprocessing & Feature Engineering
Since scientific text contains precise terminology, we avoided over-cleaning that might destroy domain-specific meaning.

**Feature Engineering:**
We utilized classical text features, focusing on lexical matching and representation:
- **TF-IDF of Claim**: Term Frequency-Inverse Document Frequency vectorization to capture key terms in the claim.
- **TF-IDF of Evidence**: TF-IDF representation of the evidence passage.
- **Cosine Similarity**: The pairwise similarity between the claim's TF-IDF vector and the evidence's TF-IDF vector, providing a strong signal of lexical overlap.
- **Length Features**: Included text length representations for both the claim and evidence.

We restricted the TF-IDF feature vocabulary to the top 5000 terms to maintain computational efficiency while capturing critical terminology. No future information or labels were used in feature generation.

## Models Tested & Model Comparison
We trained and evaluated three classical ML models:
1. **Logistic Regression (Balanced)**
2. **Linear SVM (Balanced, Probability enabled)**
3. **Random Forest (100 estimators, Balanced)**

### Evaluation Metrics
We evaluated models on Accuracy, Precision, Recall, F1-score, and Macro F1, paying close attention to Macro F1 due to class imbalance (Neutral is the majority class).

**Results on Dev Set:**
| Model | Accuracy | Macro F1 |
|-------|----------|----------|
| Logistic Regression | 0.59 | 0.4067 |
| **Linear SVM** | **0.60** | **0.4331** |
| Random Forest | 0.63 | 0.3831 |

### Confusion Matrix (Linear SVM)
```text
[[ 76  91  68]   (CONTRADICT)
 [ 79  19  33]   (NEUTRAL)
 [ 61  33 455]]  (SUPPORT)
```

### Selected Model
**Linear SVM** was selected as the best model. It achieved the highest Macro F1 score, demonstrating a better balance at recognizing the minority classes (`CONTRADICT` and `SUPPORT`) compared to Random Forest, which skewed heavily toward predicting `NEUTRAL`.

## Model Persistence (Offline Training)
The training pipeline is fully **offline**. The application does *not* train the model during user requests.

After training, the best model and the feature extraction components are serialized using `pickle` and saved to the `backend/models/` directory:
- `models/evidence_classifier.pkl`
- `models/feature_extractor.pkl`

## Inference Architecture & API Endpoint
An inference module (`ml/inference.py`) handles real-time predictions. 

**Flow:**
1. Load the serialized model and vectorizer at startup.
2. Receive a new claim and retrieved evidence texts.
3. Apply the identical preprocessing and feature extraction pipeline.
4. Predict the relationship and extract calibrated prediction probabilities (confidence).

**FastAPI Endpoint:**
`POST /api/classify`
Input:
```json
{
  "claim": "High levels of CRP lead to a higher risk of exacerbations in COPD.",
  "evidence": ["High levels of CRP were found to increase the risk of exacerbations in patients with COPD."]
}
```
Output:
```json
[
  {
    "evidence": "High levels of CRP were found to increase the risk of exacerbations in patients with COPD.",
    "prediction": "SUPPORT",
    "confidence": 0.794
  }
]
```

## Summary of Implementation & Files
- Downloaded and processed the actual SciFact dataset (`data/claims_train.jsonl`, `data/claims_dev.jsonl`, `data/corpus.jsonl`).
- Created `ml/dataset.py` for dataset extraction (SUPPORT, CONTRADICT, NEUTRAL parsing).
- Created `ml/features.py` for TF-IDF and similarity feature extraction.
- Created `ml/train.py` as an offline, runnable script to train, evaluate, and save models.
- Created `ml/inference.py` to efficiently classify new examples using the saved artifacts.
- Modified `backend/main.py` to expose the new `/api/classify` endpoint.

### Distinction & Future Phase 4
**Phase 2** retrieved relevant passages. **Phase 3** assigns a relationship label (`SUPPORT`/`CONTRADICT`/`NEUTRAL`) to each individual passage relative to the claim. 
**Phase 4** will eventually combine the results of these individual passage-level predictions to render a final verdict for the claim itself. This genuinely useful capability allows VeriSci to intelligently map exactly *why* a claim is true or false by classifying granular pieces of scientific evidence.
