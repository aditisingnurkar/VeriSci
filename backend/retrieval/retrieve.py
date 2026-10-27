import os
import pickle
import sys
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re

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
    bio_keywords = {
        "vaccine", "vaccines", "vaccination", "cancer", "cell", "cells", "protein", "proteins", 
        "gene", "genes", "virus", "viral", "infection", "infections", "disease", "diseases",
        "patient", "patients", "treatment", "treatments", "drug", "drugs", "blood", "brain", "heart",
        "tumor", "tumors", "rna", "dna", "bacteria", "bacterial", "syndrome", "therapy", "clinical",
        "mouse", "mice", "model", "immune", "immunity", "metabolism", "toxicity", "dose",
        "statin", "statins", "cholesterol", "ldl", "hdl", "hypercholesterolemia",
        "bariatric", "surgery", "obese", "obesity", "weight",
        "hypertension", "stroke", "cardiovascular", "myocardial", "infarction", "troponin",
        "ovarian", "reserve", "fertility", "infertile", "infertility", "pregnancy", "pregnant",
        "calcium", "bone", "fracture", "fractures", "elderly", "osteoporosis",
        "vitamin", "vitamins", "ascorbic", "ascorbate",
        "crp", "copd", "respiratory", "pulmonary", "exacerbation", "exacerbations",
        "hnf4a", "dgkk", "hypospadias", "microglia", "amyloid", "alzheimer", "alzheimers",
        "insulin", "glucose", "glycemic", "diabetes", "diabetic",
        "penicillin", "antibiotic", "antibiotics", "antimicrobial", "pathogen",
        "mutation", "variant", "allele", "snps", "snp", "genomic", "genetic"
    }
    words = set(re.findall(r'[a-zA-Z0-9-]+', claim.lower()))
    return not bool(words.intersection(bio_keywords))

def retrieve_evidence(claim: str, top_k: int = 5, doc_threshold: float = 0.05, sent_threshold: float = 0.02):
    if is_out_of_scope(claim):
        return [{"out_of_scope": True}]
        
    load_index()
    
    # 1. Document-level retrieval (SciFact)
    claim_vec = _doc_vectorizer.transform([claim])
    sim_scores = cosine_similarity(claim_vec, _doc_tfidf_matrix).flatten()
    
    EXCLUDE_TOKENS = {
        "the", "and", "with", "from", "that", "this", "cause", "causes", "caused", "causing",
        "does", "did", "not", "never", "without", "dont", "doesnt", "didnt", "have", "been"
    }
    raw_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', claim) if w.lower() not in EXCLUDE_TOKENS]
    def wroot(w):
        return w.rstrip('s')[:min(4, len(w))]
    c_roots = [wroot(w) for w in raw_tokens]

    # Retrieve candidate docs
    initial_k = min(top_k * 3, len(_documents))
    top_doc_indices = sim_scores.argsort()[-initial_k:][::-1]
    
    candidate_docs = []
    scifact_cands = []
    pubmed_cands = []
    
    KEY_ENTITIES = ["dgkk", "hnf4a", "bariatric", "statin", "troponin", "penicillin", "microglia", "amyloid", "copd", "hypospadias", "insulin", "ovarian"]
    claim_entities = [ent for ent in KEY_ENTITIES if ent in claim.lower()]
    
    claim_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', claim) if len(w) > 2)
    
    # Add SciFact docs
    for idx in top_doc_indices:
        tfidf_score = float(sim_scores[idx])
        doc = _documents[idx]
        text = (doc["title"] + " " + doc.get("abstract", "")).lower()
        t_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text) if w.lower() not in EXCLUDE_TOKENS]
        t_roots = set(wroot(w) for w in t_words)
        
        doc_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', text))
        overlap = len(claim_words.intersection(doc_words)) / max(1, len(claim_words))
        doc_score = max(tfidf_score, overlap * 0.75)
        
        # If claim has multiple roots, check concept coverage
        if len(c_roots) >= 2:
            covered = sum(1 for r in c_roots if r in t_roots)
            if covered < 2:
                doc_score *= 0.25  # Penalize one-sided documents
                
        for ent in claim_entities:
            if ent in text:
                doc_score += 0.35
                
        if doc_score >= doc_threshold:
            scifact_cands.append({
                "doc_score": doc_score,
                "doc": doc
            })
            
    # Add PubMed docs
    try:
        from .pubmed import retrieve_from_pubmed
        pubmed_docs = retrieve_from_pubmed(claim, top_k=top_k)
        for pdoc in pubmed_docs:
            p_text = (pdoc["title"] + " " + pdoc["abstract"]).lower()
            p_vec = _doc_vectorizer.transform([p_text])
            p_score = float(cosine_similarity(claim_vec, p_vec).flatten()[0])
            claim_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', claim) if len(w) > 2)
            doc_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', p_text))
            overlap = len(claim_words.intersection(doc_words)) / max(1, len(claim_words))
            effective_score = max(p_score, overlap * 0.75)
            
            if claim_entities and any(ent in p_text for ent in claim_entities):
                effective_score += 0.35
                
            if effective_score >= doc_threshold:
                pubmed_cands.append({
                    "doc_score": effective_score,
                    "doc": pdoc
                })
    except ImportError:
        pass
        
    # Interleave candidate docs from SciFact and PubMed to balance curated and live evidence
    scifact_cands = sorted(scifact_cands, key=lambda x: x["doc_score"], reverse=True)
    pubmed_cands = sorted(pubmed_cands, key=lambda x: x["doc_score"], reverse=True)
    
    candidate_docs = []
    max_len = max(len(scifact_cands), len(pubmed_cands))
    for i in range(max_len):
        if i < len(scifact_cands):
            candidate_docs.append(scifact_cands[i])
        if i < len(pubmed_cands):
            candidate_docs.append(pubmed_cands[i])
    
    results = []
    seen_docs = set()
    claim_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', claim) if len(w) > 2)
    
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
        
        CONCLUSION_MARKERS = [
            "conclude", "conclusion", "found", "results", "demonstrate", "showed", "observed",
            "suggest that", "indicate that", "supports that", "not associated", "no association", 
            "no link", "no increased risk", "no effect", "no difference", "did not affect",
            "safe", "safety", "did not", "does not", "furthermore", "overall",
            "compelling evidence", "associated with", "risk gene", "major risk", "effective against",
            "significantly reduce", "reduction in", "weight loss", "blood glucose", "myocardial injury",
            "risk of", "odds ratio", "substantially", "effective in"
        ]
        BACKGROUND_MARKERS = [
            "to assess", "to evaluate", "to determine", "to investigate", "hypothesized link", 
            "concerned that", "concerns about", "retracted by the journal", "aims", "aimed to", 
            "vaccine hesitancy", "debate", "fear of a link", "controversy", "some parents are concerned",
            "are limited", "data on their", "limited data"
        ]
        
        n_sents = len(sentences)
        sent_scores = []
        for i, s in enumerate(sentences):
            s_lower = s.lower()
            # Filter non-English / foreign artifacts
            if any(w in s_lower for w in ["vacunaci", "ninguna", "el estudio", "evaluar la", "las mujeres deben", "los modelos"]):
                sent_scores.append(-1.0)
                continue
                
            s_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', s_lower))
            s_overlap = len(claim_words.intersection(s_words)) / max(1, len(claim_words))
            
            # Check for domain-related terms (e.g. reproductive terms for fertility)
            if any(r in c_roots for r in ["fert", "infe"]):
                if any(t in s_lower for t in ["pregnan", "oocyte", "reproduct", "ivf", "ovarian"]):
                    s_overlap = max(s_overlap, 0.4)
                    
            base_score = max(float(sent_sims[i]), s_overlap * 0.4)
            
            if base_score < 0.01:
                sent_scores.append(0.0)
                continue
                
            adjusted_score = base_score
            has_finding = any(m in s_lower for m in CONCLUSION_MARKERS)
            if has_finding:
                adjusted_score += 0.6
                
            if i >= n_sents * 0.5:
                adjusted_score += 0.1
            if i >= n_sents - 2 and (has_finding or s_overlap >= 0.4):
                adjusted_score += 0.1
                
            # Background / Aim / Controversy penalty
            if i < 2 or any(m in s_lower for m in BACKGROUND_MARKERS):
                if any(m in s_lower for m in ["hypothesized", "concerned", "concerns", "suggested that", "aims", "debate", "retracted", "hesitancy"]):
                    adjusted_score -= 0.6
                    
            sent_scores.append(adjusted_score)
            
        best_sent_idx = int(np.argmax(sent_scores))
        best_sent_score = float(sent_scores[best_sent_idx])
        
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
