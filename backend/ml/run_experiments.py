import os
import sys
import json
import time
import pickle
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ml.unified_pipeline import UnifiedDatasetPipeline
from ml.features import FeatureExtractor

MODELS_DIR = os.path.join(BASE_DIR, "models")
BASELINE_DIR = os.path.join(MODELS_DIR, "baseline_scifact")
LABELS = ["SUPPORT", "CONTRADICT", "NEUTRAL"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def compute_detailed_metrics(y_true, y_pred, labels=LABELS) -> Dict[str, Any]:
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    per_class = {}
    for lbl in labels:
        p = precision_score(y_true, y_pred, labels=[lbl], average="macro", zero_division=0)
        r = recall_score(y_true, y_pred, labels=[lbl], average="macro", zero_division=0)
        f = f1_score(y_true, y_pred, labels=[lbl], average="macro", zero_division=0)
        per_class[lbl] = {"precision": float(p), "recall": float(r), "f1": float(f)}

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    return {
        "num_evaluated": int(len(y_true)),
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "per_class": per_class,
        "confusion_matrix": cm,
        "labels_order": labels
    }

def run_experiment_a(pipeline: UnifiedDatasetPipeline) -> Dict[str, Any]:
    """Experiment A: Existing SciFact-only Baseline Model Evaluation."""
    logging.info("=== Running Experiment A: SciFact-only Baseline ===")
    
    base_model_path = os.path.join(BASELINE_DIR, "evidence_classifier.pkl")
    base_fe_path = os.path.join(BASELINE_DIR, "feature_extractor.pkl")
    
    if not os.path.exists(base_model_path):
        base_model_path = os.path.join(MODELS_DIR, "evidence_classifier.pkl")
        base_fe_path = os.path.join(MODELS_DIR, "feature_extractor.pkl")

    with open(base_model_path, "rb") as f:
        base_model = pickle.load(f)
    with open(base_fe_path, "rb") as f:
        base_fe = pickle.load(f)

    # Evaluate on SciFact Dev (canonical baseline set)
    sf_dev = pipeline.load_scifact("dev")
    X_sf_dev = base_fe.transform(sf_dev["claim_text"], sf_dev["evidence_text"])
    y_sf_dev = sf_dev["normalized_label"]
    y_pred_sf = base_model.predict(X_sf_dev)
    metrics_sf = compute_detailed_metrics(y_sf_dev, y_pred_sf)

    # Evaluate on Combined 3-Dataset Dev to measure generalization
    comb_dev = pipeline.get_unified_dataset(["dev"], ["scifact", "healthver", "mancon"])
    X_comb_dev = base_fe.transform(comb_dev["claim_text"], comb_dev["evidence_text"])
    y_comb_dev = comb_dev["normalized_label"]
    y_pred_comb = base_model.predict(X_comb_dev)
    metrics_comb = compute_detailed_metrics(y_comb_dev, y_pred_comb)

    return {
        "experiment_name": "Experiment A (SciFact-only Baseline)",
        "model_type": str(type(base_model).__name__),
        "scifact_dev_metrics": metrics_sf,
        "combined_dev_metrics": metrics_comb
    }

def run_experiment_b(pipeline: UnifiedDatasetPipeline, X_tr, y_tr, X_dev_comb, y_dev_comb, X_dev_sf, y_dev_sf) -> Dict[str, Any]:
    """Experiment B: Three-dataset combined training on standard LR, Linear SVM, and Random Forest."""
    logging.info("=== Running Experiment B: Three-Dataset Combined Training ===")
    
    # We calibrate Linear SVM to provide predict_proba cleanly
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Linear SVM": LinearSVC(dual=False, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1)
    }

    results = {}
    best_name = None
    best_macro_f1 = -1.0
    best_model = None

    for name, model in candidates.items():
        logging.info(f"Training {name} on combined 3-dataset...")
        t0 = time.time()
        model.fit(X_tr, y_tr)
        fit_time = time.time() - t0

        y_pred_comb = model.predict(X_dev_comb)
        m_comb = compute_detailed_metrics(y_dev_comb, y_pred_comb)

        y_pred_sf = model.predict(X_dev_sf)
        m_sf = compute_detailed_metrics(y_dev_sf, y_pred_sf)

        results[name] = {
            "fit_time_seconds": fit_time,
            "combined_dev_metrics": m_comb,
            "scifact_dev_metrics": m_sf
        }

        logging.info(f"{name} -> Combined Dev Acc: {m_comb['accuracy']*100:.2f}%, Macro F1: {m_comb['macro_f1']*100:.2f}% | SciFact Dev Acc: {m_sf['accuracy']*100:.2f}%, Macro F1: {m_sf['macro_f1']*100:.2f}%")

        if m_comb["macro_f1"] > best_macro_f1:
            best_macro_f1 = m_comb["macro_f1"]
            best_name = name
            best_model = model

    return {
        "experiment_name": "Experiment B (Three-Dataset Combined Training)",
        "models_evaluated": results,
        "best_model_name": best_name,
        "best_macro_f1": best_macro_f1,
        "best_model": best_model
    }

def run_experiment_c(pipeline: UnifiedDatasetPipeline, X_tr, y_tr, X_dev_comb, y_dev_comb, X_dev_sf, y_dev_sf) -> Dict[str, Any]:
    """Experiment C: Controlled Imbalance Optimization on the Combined Model."""
    logging.info("=== Running Experiment C: Controlled Imbalance Optimization ===")

    # Test controlled class weighting and regularization variations
    weight_configs = [
        ("balanced", "balanced"),
        ("adjusted_weights", {"SUPPORT": 1.2, "CONTRADICT": 1.4, "NEUTRAL": 0.7}),
        ("boost_minority_2x", {"SUPPORT": 1.5, "CONTRADICT": 2.0, "NEUTRAL": 0.6})
    ]

    c_values = [0.05, 0.1, 0.2, 0.5, 1.0]

    results = {}
    best_config_name = None
    best_macro_f1 = -1.0
    best_clf = None

    for cw_name, cw in weight_configs:
        for C_val in c_values:
            cfg_name = f"LinearSVM_C{C_val}_{cw_name}"
            clf = LinearSVC(dual=False, C=C_val, class_weight=cw, random_state=42)
            clf.fit(X_tr, y_tr)

            y_pred_comb = clf.predict(X_dev_comb)
            m_comb = compute_detailed_metrics(y_dev_comb, y_pred_comb)

            y_pred_sf = clf.predict(X_dev_sf)
            m_sf = compute_detailed_metrics(y_dev_sf, y_pred_sf)

            results[cfg_name] = {
                "C": C_val,
                "class_weight": str(cw),
                "combined_dev_metrics": m_comb,
                "scifact_dev_metrics": m_sf
            }

            if m_comb["macro_f1"] > best_macro_f1:
                best_macro_f1 = m_comb["macro_f1"]
                best_config_name = cfg_name
                best_clf = clf

    # Also test Random Forest tuned with class weights
    rf_cfg = "RandomForest_100_balanced"
    rf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    rf_comb = compute_detailed_metrics(y_dev_comb, rf.predict(X_dev_comb))
    rf_sf = compute_detailed_metrics(y_dev_sf, rf.predict(X_dev_sf))
    results[rf_cfg] = {
        "C": None,
        "class_weight": "balanced",
        "combined_dev_metrics": rf_comb,
        "scifact_dev_metrics": rf_sf
    }
    if rf_comb["macro_f1"] > best_macro_f1:
        best_macro_f1 = rf_comb["macro_f1"]
        best_config_name = rf_cfg
        best_clf = rf

    logging.info(f"Best Experiment C Configuration: {best_config_name} with Combined Macro F1 = {best_macro_f1*100:.2f}%")

    # If the winning classifier is a LinearSVM, wrap in a calibrated classifier using prefit or cv=2 for inference probabilities
    if isinstance(best_clf, LinearSVC):
        logging.info("Calibrating LinearSVC probabilities with cv=2...")
        winning_model = CalibratedClassifierCV(best_clf, cv=2)
        winning_model.fit(X_tr, y_tr)
    else:
        winning_model = best_clf

    # Compute final metrics on both dev sets
    comb_metrics = compute_detailed_metrics(y_dev_comb, best_clf.predict(X_dev_comb))
    sf_metrics = compute_detailed_metrics(y_dev_sf, best_clf.predict(X_dev_sf))

    return {
        "experiment_name": "Experiment C (Controlled Imbalance Optimization)",
        "all_configurations": results,
        "best_config_name": best_config_name,
        "best_macro_f1": best_macro_f1,
        "best_raw_model": best_clf,
        "final_deployable_model": winning_model,
        "best_combined_metrics": comb_metrics,
        "best_scifact_metrics": sf_metrics
    }

def main():
    pipeline = UnifiedDatasetPipeline()
    
    logging.info("Loading training and development datasets...")
    train_df = pipeline.get_unified_dataset(["train"], ["scifact", "healthver", "mancon"])
    comb_dev = pipeline.get_unified_dataset(["dev"], ["scifact", "healthver", "mancon"])
    sf_dev = pipeline.load_scifact("dev")

    logging.info(f"Dataset sizes -> Combined Train: {len(train_df)}, Combined Dev: {len(comb_dev)}, SciFact Dev: {len(sf_dev)}")

    # Feature extraction fitted on combined training data
    logging.info("Fitting feature extractor on combined training data...")
    fe = FeatureExtractor()
    fe.fit(train_df["claim_text"], train_df["evidence_text"])

    X_tr = fe.transform(train_df["claim_text"], train_df["evidence_text"])
    y_tr = train_df["normalized_label"]

    X_dev_comb = fe.transform(comb_dev["claim_text"], comb_dev["evidence_text"])
    y_dev_comb = comb_dev["normalized_label"]

    X_dev_sf = fe.transform(sf_dev["claim_text"], sf_dev["evidence_text"])
    y_dev_sf = sf_dev["normalized_label"]

    # 1. Experiment A
    exp_a = run_experiment_a(pipeline)

    # 2. Experiment B
    exp_b = run_experiment_b(pipeline, X_tr, y_tr, X_dev_comb, y_dev_comb, X_dev_sf, y_dev_sf)

    # 3. Experiment C
    exp_c = run_experiment_c(pipeline, X_tr, y_tr, X_dev_comb, y_dev_comb, X_dev_sf, y_dev_sf)

    # Deployable winning model
    final_model = exp_c["final_deployable_model"]

    # Save final model and extractor to backend/models
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_save_path = os.path.join(MODELS_DIR, "evidence_classifier.pkl")
    extractor_save_path = os.path.join(MODELS_DIR, "feature_extractor.pkl")
    metadata_save_path = os.path.join(MODELS_DIR, "model_metadata.json")

    logging.info(f"Saving final optimized model to {model_save_path}...")
    with open(model_save_path, "wb") as f:
        pickle.dump(final_model, f)
    with open(extractor_save_path, "wb") as f:
        pickle.dump(fe, f)

    metadata = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_datasets": ["SciFact", "HealthVer", "ManConCorpus"],
        "training_samples_total": len(train_df),
        "training_distribution": train_df["normalized_label"].value_counts().to_dict(),
        "selected_model": exp_c["best_config_name"],
        "feature_extractor": "FeatureExtractor (TF-IDF 5000 + similarity + length + overlap + negation cues)",
        "label_mapping": {
            "SciFact": "SUPPORT / CONTRADICT / NEUTRAL",
            "HealthVer": "Supports->SUPPORT, Refutes->CONTRADICT, Neutral->NEUTRAL",
            "ManConCorpus": "ENTAILMENT->SUPPORT, CONTRADICTION->CONTRADICT, NEUTRAL->NEUTRAL"
        },
        "experiment_a_baseline": exp_a,
        "experiment_b_combined": {
            "best_model_name": exp_b["best_model_name"],
            "best_macro_f1": exp_b["best_macro_f1"],
            "models_evaluated": exp_b["models_evaluated"]
        },
        "experiment_c_optimized": {
            "best_config": exp_c["best_config_name"],
            "best_combined_metrics": exp_c["best_combined_metrics"],
            "best_scifact_metrics": exp_c["best_scifact_metrics"]
        }
    }

    with open(metadata_save_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logging.info("Saved experiment metadata and final model successfully.")

    # Print summary tables
    print("\n" + "="*80)
    print("EXPERIMENT COMPARISON SUMMARY: COMBINED 3-DATASET EVALUATION (N=4,599)")
    print("="*80)
    base_comb = exp_a["combined_dev_metrics"]
    opt_comb = exp_c["best_combined_metrics"]
    
    print(f"{'Metric':<20} | {'SciFact Baseline':<18} | {'Optimized 3-Dataset':<20} | {'Difference':<15}")
    print("-" * 80)
    acc_diff = (opt_comb['accuracy'] - base_comb['accuracy']) * 100
    mf1_diff = (opt_comb['macro_f1'] - base_comb['macro_f1']) * 100
    wf1_diff = (opt_comb['weighted_f1'] - base_comb['weighted_f1']) * 100
    print(f"{'Accuracy':<20} | {base_comb['accuracy']*100:>16.2f}% | {opt_comb['accuracy']*100:>18.2f}% | {acc_diff:>+13.2f}%")
    print(f"{'Macro F1':<20} | {base_comb['macro_f1']*100:>16.2f}% | {opt_comb['macro_f1']*100:>18.2f}% | {mf1_diff:>+13.2f}%")
    print(f"{'Weighted F1':<20} | {base_comb['weighted_f1']*100:>16.2f}% | {opt_comb['weighted_f1']*100:>18.2f}% | {wf1_diff:>+13.2f}%")
    
    for lbl in LABELS:
        b_f1 = base_comb["per_class"][lbl]["f1"] * 100
        o_f1 = opt_comb["per_class"][lbl]["f1"] * 100
        d_f1 = o_f1 - b_f1
        print(f"{lbl + ' F1':<20} | {b_f1:>16.2f}% | {o_f1:>18.2f}% | {d_f1:>+13.2f}%")

    print("\n" + "="*80)
    print("EXPERIMENT COMPARISON SUMMARY: SCIFACT HELD-OUT DEV EVALUATION (N=2,294)")
    print("="*80)
    base_sf = exp_a["scifact_dev_metrics"]
    opt_sf = exp_c["best_scifact_metrics"]
    print(f"{'Metric':<20} | {'SciFact Baseline':<18} | {'Optimized 3-Dataset':<20} | {'Difference':<15}")
    print("-" * 80)
    acc_diff_sf = (opt_sf['accuracy'] - base_sf['accuracy']) * 100
    mf1_diff_sf = (opt_sf['macro_f1'] - base_sf['macro_f1']) * 100
    wf1_diff_sf = (opt_sf['weighted_f1'] - base_sf['weighted_f1']) * 100
    print(f"{'Accuracy':<20} | {base_sf['accuracy']*100:>16.2f}% | {opt_sf['accuracy']*100:>18.2f}% | {acc_diff_sf:>+13.2f}%")
    print(f"{'Macro F1':<20} | {base_sf['macro_f1']*100:>16.2f}% | {opt_sf['macro_f1']*100:>18.2f}% | {mf1_diff_sf:>+13.2f}%")
    print(f"{'Weighted F1':<20} | {base_sf['weighted_f1']*100:>16.2f}% | {opt_sf['weighted_f1']*100:>18.2f}% | {wf1_diff_sf:>+13.2f}%")
    for lbl in LABELS:
        b_f1 = base_sf["per_class"][lbl]["f1"] * 100
        o_f1 = opt_sf["per_class"][lbl]["f1"] * 100
        d_f1 = o_f1 - b_f1
        print(f"{lbl + ' F1':<20} | {b_f1:>16.2f}% | {o_f1:>18.2f}% | {d_f1:>+13.2f}%")

if __name__ == "__main__":
    main()
