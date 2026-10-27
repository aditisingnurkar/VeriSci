import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "unsupervised")
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# In-memory singleton cache
_embedding_model = None
_embedding_cache: Dict[str, np.ndarray] = {}

def get_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL):
    """
    Initializes and caches the SentenceTransformer model singleton.
    Model: sentence-transformers/all-MiniLM-L6-v2
    License: Apache 2.0
    Dimension: 384
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading SentenceTransformer: {model_name}")
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model

def format_claim_evidence(claim: str, evidence: str) -> str:
    """Standardized claim-evidence representation for semantic embeddings."""
    return f"Claim: {claim.strip()}\nEvidence: {evidence.strip()}"

def encode_pairs(pairs: List[Tuple[str, str]], model_name: str = DEFAULT_EMBEDDING_MODEL, batch_size: int = 64) -> np.ndarray:
    """
    Generates semantic embeddings for a list of (claim, evidence) tuples.
    Leverages in-memory cache to prevent re-encoding identical pairs.
    """
    model = get_embedding_model(model_name)
    
    formatted_texts = [format_claim_evidence(c, e) for c, e in pairs]
    uncached_indices = []
    uncached_texts = []
    
    embeddings = [None] * len(formatted_texts)
    
    for idx, text in enumerate(formatted_texts):
        if text in _embedding_cache:
            embeddings[idx] = _embedding_cache[text]
        else:
            uncached_indices.append(idx)
            uncached_texts.append(text)
            
    if uncached_texts:
        logger.info(f"Encoding {len(uncached_texts)} new claim-evidence pairs...")
        new_embs = model.encode(uncached_texts, batch_size=batch_size, show_progress_bar=len(uncached_texts) > 200, normalize_embeddings=True)
        for idx, emb in zip(uncached_indices, new_embs):
            _embedding_cache[uncached_texts[uncached_indices.index(idx)]] = emb
            embeddings[idx] = emb
            
    return np.array(embeddings, dtype=np.float32)

class UnsupervisedStanceModel:
    """
    Unsupervised Stance Model using K-Means (k=3) over sentence-transformer embeddings.
    
    IMPORTANT:
    1. K-Means is fitted WITHOUT labels. Cluster IDs (0, 1, 2) are arbitrary.
    2. A post-hoc mapping to stance labels (SUPPORT, CONTRADICT, NEUTRAL) is derived
       using a separate labelled validation split.
    3. Distance to centroid represents geometric proximity in embedding space,
       NOT a calibrated statistical probability.
    """
    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.kmeans = None
        self.metadata = {}
        self.mapping_data = {}
        self.cluster_to_stance = {}
        self.is_loaded = False
        
    def load(self) -> bool:
        """Loads fitted KMeans model, metadata, and post-hoc validation mapping."""
        kmeans_path = os.path.join(self.models_dir, "kmeans_model.pkl")
        meta_path = os.path.join(self.models_dir, "metadata.json")
        mapping_path = os.path.join(self.models_dir, "cluster_mapping.json")
        
        if not os.path.exists(kmeans_path):
            logger.warning(f"KMeans model not found at {kmeans_path}")
            return False
            
        with open(kmeans_path, "rb") as f:
            self.kmeans = pickle.load(f)
            
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
                
        if os.path.exists(mapping_path):
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.mapping_data = json.load(f)
                self.cluster_to_stance = {
                    int(k): v for k, v in self.mapping_data.get("cluster_to_stance", {}).items()
                }
                
        self.is_loaded = True
        logger.info(f"Loaded Unsupervised K-Means model (k={self.kmeans.n_clusters}) from {self.models_dir}")
        return True

    @property
    def cluster_mapping(self) -> Dict[str, str]:
        return {str(k): v for k, v in self.cluster_to_stance.items()}

    def predict_single(self, claim: str, evidence: str) -> Dict[str, Any]:
        """Runs unsupervised inference for a single claim-evidence pair."""
        return self.predict_batch(claim, [evidence])[0]

    def predict_batch(self, claim: str, evidence_texts: List[str]) -> List[Dict[str, Any]]:
        """
        Runs unsupervised clustering inference for a claim against multiple evidence texts.
        
        Returns:
            List of dicts containing:
            - cluster_id (int): 0, 1, or 2
            - centroid_distance (float): Euclidean distance to assigned cluster centroid
            - mapped_stance (str): 'SUPPORT', 'CONTRADICT', 'NEUTRAL', or 'UNCERTAIN'
            - prediction (str): alias for mapped_stance
            - confidence (float): alias for cluster_affinity
            - is_unsupervised (bool): True
            - cluster_affinity (float): 1 / (1 + distance), geometric proximity
            - all_distances (List[float]): distances to all 3 centroids
        """
        if not self.is_loaded:
            if not self.load():
                # Safe fallback if model not trained yet
                return [{
                    "cluster_id": -1,
                    "centroid_distance": 1.0,
                    "mapped_stance": "NEUTRAL",
                    "prediction": "NEUTRAL",
                    "confidence": 0.5,
                    "cluster_affinity": 0.5,
                    "is_unsupervised": True,
                    "all_distances": [1.0, 1.0, 1.0],
                    "status": "UNSUPERVISED_MODEL_NOT_FITTED"
                } for _ in evidence_texts]

        if not evidence_texts:
            return []

        pairs = [(claim, ev) for ev in evidence_texts]
        embeddings = encode_pairs(pairs, model_name=self.metadata.get("embedding_model", DEFAULT_EMBEDDING_MODEL))
        
        results = []
        cluster_centers = self.kmeans.cluster_centers_
        
        for idx in range(len(evidence_texts)):
            emb = embeddings[idx]
            # Compute distances to all centroids
            distances = [float(np.linalg.norm(emb - c)) for c in cluster_centers]
            assigned_cluster = int(np.argmin(distances))
            min_dist = distances[assigned_cluster]
            
            # Post-hoc validation mapping
            mapped_stance = self.cluster_to_stance.get(assigned_cluster, "UNCERTAIN")
            
            # Geometric affinity score (not a class probability)
            # In normalized space, distance is between 0 and 2; affinity is between 0.33 and 1.0
            affinity = float(1.0 / (1.0 + min_dist))
            
            # Cluster purity / validation confidence if available
            purity = self.mapping_data.get("cluster_purities", {}).get(str(assigned_cluster), 0.50)
            
            results.append({
                "cluster_id": assigned_cluster,
                "centroid_distance": round(min_dist, 4),
                "mapped_stance": mapped_stance,
                "prediction": mapped_stance,
                "confidence": round(affinity, 4),
                "cluster_affinity": round(affinity, 4),
                "is_unsupervised": True,
                "stance_source": "unsupervised_cluster_mapping",
                "validation_purity": round(purity, 4),
                "all_distances": [round(d, 4) for d in distances]
            })
            
        return results

# Singleton instance
unsupervised_model = UnsupervisedStanceModel()

def get_unsupervised_model() -> UnsupervisedStanceModel:
    """Returns the singleton UnsupervisedStanceModel instance."""
    return unsupervised_model

