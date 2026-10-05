import os
import pickle
import sys
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

INDEX_DIR = os.path.join(os.path.dirname(__file__), "saved_index")

_doc_vectorizer = None
_doc_tfidf_matrix = None
_documents = None

def load_index():
    global _doc_vectorizer, _doc_tfidf_matrix, _documents
    if _doc_vectorizer is None:
        if not os.path.exists(os.path.join(INDEX_DIR, 'doc_vectorizer.pkl')):
            raise FileNotFoundError("Index not found. Please run index.py first.")
            
        with open(os.path.join(INDEX_DIR, 'doc_vectorizer.pkl'), 'rb') as f:
            _doc_vectorizer = pickle.load(f)
        with open(os.path.join(INDEX_DIR, 'doc_tfidf_matrix.pkl'), 'rb') as f:
            _doc_tfidf_matrix = pickle.load(f)
        with open(os.path.join(INDEX_DIR, 'documents.pkl'), 'rb') as f:
            _documents = pickle.load(f)

def retrieve_evidence(claim: str, top_k: int = 5, doc_threshold: float = 0.05, sent_threshold: float = 0.02):
    load_index()
    
    # 1. Document-level retrieval
    claim_vec = _doc_vectorizer.transform([claim])
    sim_scores = cosine_similarity(claim_vec, _doc_tfidf_matrix).flatten()
    
    # We retrieve slightly more docs first
    initial_k = min(top_k * 3, len(_documents))
    top_doc_indices = sim_scores.argsort()[-initial_k:][::-1]
    
    results = []
    
    for idx in top_doc_indices:
        doc_score = float(sim_scores[idx])
        if doc_score < doc_threshold:
            continue
            
        doc = _documents[idx]
        sentences = doc["sentences"]
        
        if not sentences:
            continue
            
        # 2. Sentence-level retrieval within the doc
        sent_vecs = _doc_vectorizer.transform(sentences)
        sent_sims = cosine_similarity(claim_vec, sent_vecs).flatten()
        best_sent_idx = int(sent_sims.argmax())
        best_sent_score = float(sent_sims[best_sent_idx])
        
        if best_sent_score < sent_threshold:
            continue
            
        results.append({
            "doc_id": str(doc["doc_id"]),
            "title": doc["title"],
            "evidence_text": sentences[best_sent_idx],
            "sentence_idx": best_sent_idx,
            "relevance_score": doc_score * 0.5 + best_sent_score * 0.5,
            "source": "SciFact"
        })
        
        # Distinct documents
        if len(results) >= top_k:
            break
            
    return results
