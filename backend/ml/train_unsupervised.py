import os
import sys
import json
import pickle
import logging
import argparse
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    silhouette_score,
    accuracy_score,
    classification_report,
    confusion_matrix
)
from scipy.optimize import linear_sum_assignment

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ml.dataset import get_three_dataset_data, get_train_dev_data
from ml.unsupervised_model import encode_pairs, DEFAULT_EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models", "unsupervised")
EVAL_DIR = os.path.join(BASE_DIR, "eval")

def derive_post_hoc_mapping(y_true: List[str], cluster_ids: List[int], label_names: List[str] = ["SUPPORT", "CONTRADICT", "NEUTRAL"]) -> Tuple[Dict[int, str], Dict[str, Any]]:
    """
    Derives an optimal post-hoc cluster-to-stance mapping on labelled validation data.
    Uses Hungarian algorithm (linear_sum_assignment) on the contingency matrix to find
    the maximum-weight bipartite matching between clusters and stance labels.
    
    CRITICAL NOTE:
    The mapping is computed on validation data AFTER unsupervised fitting.
    The clustering itself never saw these labels.
    """
    contingency = {}
    n_clusters = len(set(cluster_ids))
    
    # Build contingency matrix
    matrix = np.zeros((n_clusters, len(label_names)), dtype=int)
    label_to_idx = {lbl: idx for idx, lbl in enumerate(label_names)}
    
    for c_id, true_lbl in zip(cluster_ids, y_true):
        if c_id not in contingency:
            contingency[c_id] = {lbl: 0 for lbl in label_names}
        contingency[c_id][true_lbl] += 1
        matrix[c_id][label_to_idx[true_lbl]] += 1
        
    # Solve maximum bipartite matching (negate matrix for linear_sum_assignment)
    row_ind, col_ind = linear_sum_assignment(-matrix)
    
    mapping = {}
    purities = {}
    
    for r, c in zip(row_ind, col_ind):
        cluster_id = int(r)
        assigned_label = label_names[c]
        mapping[cluster_id] = assigned_label
        
        total_cluster_samples = int(np.sum(matrix[r]))
        majority_samples = int(matrix[r][c])
        purity = float(majority_samples / total_cluster_samples) if total_cluster_samples > 0 else 0.0
        purities[str(cluster_id)] = round(purity, 4)
        
    # Contingency report formatted as standard dict
    formatted_contingency = {
        str(k): v for k, v in contingency.items()
    }
    
    meta = {
        "contingency_matrix": formatted_contingency,
        "cluster_purities": purities,
        "mapping_method": "Hungarian bipartite maximum matching on validation split"
    }
    
    return mapping, meta

def train_unsupervised(
    n_clusters: int = 3,
    sample_limit: Optional[int] = None,
    scifact_only: bool = False,
    random_state: int = 42
):
    """
    Trains the Unsupervised K-Means clustering model without labels.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(EVAL_DIR, exist_ok=True)
    
    logger.info("=== STEP 1: Loading Training Data for Unsupervised Clustering ===")
    if scifact_only:
        logger.info("Loading SciFact dataset...")
        train_df, dev_df = get_train_dev_data(DATA_DIR)
    else:
        logger.info("Loading Three-Dataset Combined Data (SciFact + HealthVer + ManConCorpus)...")
        train_df, dev_df = get_three_dataset_data(DATA_DIR)
        
    if sample_limit and sample_limit < len(train_df):
        logger.info(f"Subsampling training data to {sample_limit} examples for speed...")
        train_df = train_df.sample(sample_limit, random_state=random_state)
        
    logger.info(f"Training corpus size: {len(train_df)} claim-evidence pairs")
    logger.info(f"Validation corpus size: {len(dev_df)} claim-evidence pairs")
    
    # Verify that we discard labels for K-Means fitting
    train_pairs = list(zip(train_df['claim'].astype(str), train_df['evidence_text'].astype(str)))
    dev_pairs = list(zip(dev_df['claim'].astype(str), dev_df['evidence_text'].astype(str)))
    y_dev = list(dev_df['label'].astype(str))
    
    logger.info(f"=== STEP 2: Generating Semantic Embeddings with {DEFAULT_EMBEDDING_MODEL} ===")
    X_train_emb = encode_pairs(train_pairs, model_name=DEFAULT_EMBEDDING_MODEL)
    logger.info(f"Generated training embeddings: shape {X_train_emb.shape}")
    
    logger.info(f"=== STEP 3: Fitting K-Means (k={n_clusters}, random_state={random_state}) WITHOUT LABELS ===")
    kmeans = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        max_iter=300,
        random_state=random_state
    )
    # FIT WITHOUT LABELS: K-Means only clusters geometric features
    kmeans.fit(X_train_emb)
    logger.info(f"K-Means fit complete. Inertia: {kmeans.inertia_:.2f}")
    
    logger.info("=== STEP 4: Evaluating Clustering on Validation Split ===")
    X_dev_emb = encode_pairs(dev_pairs, model_name=DEFAULT_EMBEDDING_MODEL)
    dev_clusters = kmeans.predict(X_dev_emb).tolist()
    
    # 1. Strictest Unsupervised Metrics (No labels used during calculation)
    # Silhouette score on a subsample of validation embeddings to keep calculation fast
    sub_size = min(3000, len(X_dev_emb))
    sil_score = float(silhouette_score(X_dev_emb[:sub_size], dev_clusters[:sub_size]))
    logger.info(f"Validation Silhouette Score (subsample {sub_size}): {sil_score:.4f}")
    
    # 2. Cluster Quality relative to ground-truth (ARI & NMI)
    ari = float(adjusted_rand_score(y_dev, dev_clusters))
    nmi = float(normalized_mutual_info_score(y_dev, dev_clusters))
    logger.info(f"Validation Adjusted Rand Index (ARI): {ari:.4f}")
    logger.info(f"Validation Normalized Mutual Information (NMI): {nmi:.4f}")
    
    # 3. Post-Hoc Cluster-to-Stance Mapping
    mapping, mapping_meta = derive_post_hoc_mapping(y_dev, dev_clusters)
    mapped_predictions = [mapping[c] for c in dev_clusters]
    
    val_acc = float(accuracy_score(y_dev, mapped_predictions))
    val_report = classification_report(y_dev, mapped_predictions, output_dict=True, zero_division=0)
    
    logger.info(f"Post-hoc Validation Mapping: {mapping}")
    logger.info(f"Post-hoc Validation Mapped Accuracy: {val_acc * 100:.2f}%")
    logger.info(f"Post-hoc Validation Macro F1: {val_report['macro avg']['f1-score']:.4f}")
    
    # Cluster distributions
    cluster_counts = {int(k): int(v) for k, v in pd.Series(dev_clusters).value_counts().items()}
    
    # Save artifacts
    logger.info("=== STEP 5: Persisting Unsupervised Model Artifacts ===")
    with open(os.path.join(MODELS_DIR, "kmeans_model.pkl"), "wb") as f:
        pickle.dump(kmeans, f)
        
    metadata = {
        "algorithm": "K-Means Clustering",
        "embedding_model": DEFAULT_EMBEDDING_MODEL,
        "embedding_dim": int(X_train_emb.shape[1]),
        "n_clusters": n_clusters,
        "random_state": random_state,
        "inertia": float(kmeans.inertia_),
        "training_samples": len(train_df),
        "dataset_source": "SciFact-only" if scifact_only else "SciFact + HealthVer + ManConCorpus",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "license": "Apache 2.0 (SentenceTransformers all-MiniLM-L6-v2) + MIT (VeriSci)"
    }
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    cluster_mapping_payload = {
        "cluster_to_stance": {str(k): v for k, v in mapping.items()},
        "cluster_purities": mapping_meta["cluster_purities"],
        "contingency_table": mapping_meta["contingency_matrix"],
        "validation_metrics": {
            "silhouette_score": round(sil_score, 4),
            "adjusted_rand_index": round(ari, 4),
            "normalized_mutual_info": round(nmi, 4),
            "mapped_accuracy": round(val_acc, 4),
            "mapped_macro_f1": round(val_report['macro avg']['f1-score'], 4),
            "cluster_distribution": cluster_counts
        },
        "is_post_hoc_validation_derived": True,
        "derived_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(os.path.join(MODELS_DIR, "cluster_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(cluster_mapping_payload, f, indent=2)
        
    logger.info("Training and validation complete. Models saved successfully.")
    return metadata, cluster_mapping_payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Unsupervised K-Means Stance Clustering Model")
    parser.add_argument("--clusters", type=int, default=3, help="Number of clusters (default: 3)")
    parser.add_argument("--sample-limit", type=int, default=None, help="Optional training sample limit")
    parser.add_argument("--scifact-only", action="store_true", help="Train on SciFact only")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed")
    args = parser.parse_args()
    
    train_unsupervised(
        n_clusters=args.clusters,
        sample_limit=args.sample_limit,
        scifact_only=args.scifact_only,
        random_state=args.seed
    )
