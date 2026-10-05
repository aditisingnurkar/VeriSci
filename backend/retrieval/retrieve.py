import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

INDEX_DIR = os.path.join(os.path.dirname(__file__), "saved_index")

_vectorizer = None
_tfidf_matrix = None
_passages = None

def load_index():
    global _vectorizer, _tfidf_matrix, _passages
    if _vectorizer is None:
        if not os.path.exists(os.path.join(INDEX_DIR, 'vectorizer.pkl')):
            raise FileNotFoundError("Index not found. Please run index.py first.")
            
        with open(os.path.join(INDEX_DIR, 'vectorizer.pkl'), 'rb') as f:
            _vectorizer = pickle.load(f)
        with open(os.path.join(INDEX_DIR, 'tfidf_matrix.pkl'), 'rb') as f:
            _tfidf_matrix = pickle.load(f)
        with open(os.path.join(INDEX_DIR, 'passages.pkl'), 'rb') as f:
            _passages = pickle.load(f)

def retrieve_evidence(claim: str, top_k: int = 5):
    load_index()
    
    # Transform claim
    claim_vec = _vectorizer.transform([claim])
    
    # Compute similarity
    sim_scores = cosine_similarity(claim_vec, _tfidf_matrix).flatten()
    
    # Get top_k indices
    top_indices = sim_scores.argsort()[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        score = float(sim_scores[idx])
        if score > 0.0:  # Only return if there's some similarity
            passage = _passages[idx]
            results.append({
                "document_id": str(passage["doc_id"]),
                "title": passage["title"],
                "evidence_text": passage["text"],
                "relevance_score": score,
                "source": "SciFact"
            })
            
    return results
