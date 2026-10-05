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

def is_out_of_scope(claim: str) -> bool:
    # A simple heuristic check for biomedical/health terms
    # If the claim contains any of these, we consider it in scope even if no evidence is found.
    # Otherwise, if no evidence is found and it doesn't contain these, it's OUT_OF_SCOPE.
    bio_keywords = {
        "vaccine", "cancer", "cell", "protein", "gene", "virus", "infection", 
        "disease", "patient", "treatment", "drug", "blood", "brain", "heart",
        "tumor", "rna", "dna", "bacteria", "syndrome", "therapy", "clinical",
        "mouse", "mice", "model", "immune", "metabolism", "toxicity", "dose"
    }
    words = set(claim.lower().replace(".", "").replace(",", "").split())
    return not bool(words.intersection(bio_keywords))

def retrieve_evidence(claim: str, top_k: int = 5, doc_threshold: float = 0.05, sent_threshold: float = 0.02):
    load_index()
    
    # 1. Document-level retrieval (SciFact)
    claim_vec = _doc_vectorizer.transform([claim])
    sim_scores = cosine_similarity(claim_vec, _doc_tfidf_matrix).flatten()
    
    # Retrieve more docs first
    initial_k = min(top_k * 3, len(_documents))
    top_doc_indices = sim_scores.argsort()[-initial_k:][::-1]
    
    candidate_docs = []
    
    # Add SciFact docs
    for idx in top_doc_indices:
        doc_score = float(sim_scores[idx])
        if doc_score >= doc_threshold:
            doc = _documents[idx]
            candidate_docs.append({
                "doc_score": doc_score,
                "doc": doc
            })
            
    # Add PubMed docs
    try:
        from .pubmed import retrieve_from_pubmed
        pubmed_docs = retrieve_from_pubmed(claim, top_k=top_k)
        for pdoc in pubmed_docs:
            # Score PubMed docs using our vectorizer to keep scores comparable
            p_vec = _doc_vectorizer.transform([pdoc["title"] + " " + pdoc["abstract"]])
            p_score = float(cosine_similarity(claim_vec, p_vec).flatten()[0])
            if p_score >= doc_threshold:
                candidate_docs.append({
                    "doc_score": p_score,
                    "doc": pdoc
                })
    except ImportError:
        pass
        
    # Sort combined candidate docs by doc_score
    candidate_docs = sorted(candidate_docs, key=lambda x: x["doc_score"], reverse=True)
    
    results = []
    seen_docs = set()
    
    for cdoc in candidate_docs:
        doc_score = cdoc["doc_score"]
        doc = cdoc["doc"]
        doc_id = str(doc["doc_id"])
        
        if doc_id in seen_docs:
            continue
            
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
            
        context_before = sentences[best_sent_idx - 1] if best_sent_idx > 0 else ""
        context_after = sentences[best_sent_idx + 1] if best_sent_idx < len(sentences) - 1 else ""
            
        results.append({
            "doc_id": doc_id,
            "title": doc["title"],
            "evidence_text": sentences[best_sent_idx],
            "context_before": context_before,
            "context_after": context_after,
            "sentence_idx": best_sent_idx,
            "relevance_score": doc_score * 0.5 + best_sent_score * 0.5,
            "source": doc.get("source", "SciFact"),
            "url": doc.get("url", "")
        })
        seen_docs.add(doc_id)
        
        if len(results) >= top_k:
            break
            
    if not results:
        if is_out_of_scope(claim):
            return [{"out_of_scope": True}]
            
    return results
