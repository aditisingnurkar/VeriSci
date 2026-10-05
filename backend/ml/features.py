import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class FeatureExtractor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.negation_cues = ["not", "no", "without", "fail", "lack", "unchanged", "reduced", "increased", "decreased"]
        
    def fit(self, claims, evidences):
        texts = claims.tolist() + evidences.tolist()
        self.vectorizer.fit(texts)
        
    def transform(self, claims, evidences):
        claim_tfidf = self.vectorizer.transform(claims)
        evidence_tfidf = self.vectorizer.transform(evidences)
        
        similarities = claim_tfidf.multiply(evidence_tfidf).sum(axis=1) # (N, 1) matrix
        
        claim_lens = np.array([len(c.split()) for c in claims]).reshape(-1, 1)
        evidence_lens = np.array([len(e.split()) for e in evidences]).reshape(-1, 1)
        
        # Word overlap
        overlap = []
        for c, e in zip(claims, evidences):
            c_words = set(c.lower().split())
            e_words = set(e.lower().split())
            overlap.append(len(c_words.intersection(e_words)) / max(1, len(c_words)))
        overlap = np.array(overlap).reshape(-1, 1)
        
        # Negation cue flags
        neg_flags = []
        for c, e in zip(claims, evidences):
            c_lower = c.lower()
            e_lower = e.lower()
            flags = []
            for cue in self.negation_cues:
                flags.append(1 if cue in c_lower else 0)
                flags.append(1 if cue in e_lower else 0)
            neg_flags.append(flags)
        neg_flags = np.array(neg_flags)
        
        features = sp.hstack([
            claim_tfidf, 
            evidence_tfidf, 
            similarities,
            claim_lens,
            evidence_lens,
            overlap,
            neg_flags
        ])
        
        return features
