import os
import pickle
import numpy as np
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
UNSUPERVISED_DIR = os.path.join(MODELS_DIR, "unsupervised")

from ml.unsupervised_model import unsupervised_model

class UnsupervisedEvidenceClassifier:
    """
    Project B: Unsupervised Stance Analysis Classifier.
    
    Replaces supervised Random Forest / DistilRoBERTa with K-Means (k=3)
    over dense sentence-transformer embeddings (all-MiniLM-L6-v2).
    
    Adheres strictly to AIML unsupervised criteria:
    - Fits without labels.
    - Maps cluster IDs to stances via a post-hoc validation matrix.
    - Distinguishes centroid distance from statistical probability.
    """
    def __init__(self):
        self.model = unsupervised_model
        
    def load(self):
        return self.model.load()
        
    def predict(self, claim: str, evidence_texts: List[str], titles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Runs unsupervised clustering on claim-evidence pairs.
        """
        if not evidence_texts:
            return []
            
        cluster_results = self.model.predict_batch(claim, evidence_texts)
        
        # Topical anchor check: absence of evidence vs evidence of absence
        import re
        EXCLUDE_WORDS = {"the", "and", "for", "with", "that", "this", "from", "are", "can", "may", "will", "level", "levels"}
        c_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", claim.lower()) if w.lower() not in EXCLUDE_WORDS]
        
        final_results = []
        for idx, res in enumerate(cluster_results):
            ev_text = evidence_texts[idx]
            doc_title = str(titles[idx]).lower() if (titles and idx < len(titles)) else ""
            full_context = f"{doc_title} {ev_text}".lower()
            
            # If evidence has zero topical overlap with claim words, preserve safe NEUTRAL
            has_overlap = any(w in full_context for w in c_words) if c_words else True
            
            if not has_overlap:
                final_results.append({
                    "prediction": "NEUTRAL",
                    "confidence": 0.95,
                    "cluster_id": res["cluster_id"],
                    "centroid_distance": res["centroid_distance"],
                    "cluster_affinity": res["cluster_affinity"],
                    "is_unsupervised": True,
                    "stance_source": "topical_filter_neutral",
                    "validation_purity": res.get("validation_purity", 0.5),
                    "all_distances": res.get("all_distances", [])
                })
            else:
                final_results.append({
                    "prediction": res["mapped_stance"],
                    "confidence": res["cluster_affinity"],
                    "cluster_id": res["cluster_id"],
                    "centroid_distance": res["centroid_distance"],
                    "cluster_affinity": res["cluster_affinity"],
                    "is_unsupervised": True,
                    "stance_source": "unsupervised_cluster_mapping",
                    "validation_purity": res.get("validation_purity", 0.5),
                    "all_distances": res.get("all_distances", [])
                })
                
        return final_results

# Primary inference singleton for Project B
classifier = UnsupervisedEvidenceClassifier()

def classify_evidence(claim: str, evidence_texts: List[str], titles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Primary interface called by main.py verification pipeline."""
    return classifier.predict(claim, evidence_texts, titles=titles)
