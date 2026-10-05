import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FeatureExtractor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        
    def fit(self, claims, evidences):
        texts = claims.tolist() + evidences.tolist()
        self.vectorizer.fit(texts)
        
    def transform(self, claims, evidences):
        claim_tfidf = self.vectorizer.transform(claims)
        evidence_tfidf = self.vectorizer.transform(evidences)
        
        # Calculate cosine similarity for each pair
        # We can do this efficiently by computing row-wise dot products if normalized,
        # but TfidfVectorizer returns normalized vectors by default.
        similarities = claim_tfidf.multiply(evidence_tfidf).sum(axis=1) # (N, 1) matrix
        
        # We can also compute length differences
        claim_lens = np.array([len(c.split()) for c in claims]).reshape(-1, 1)
        evidence_lens = np.array([len(e.split()) for e in evidences]).reshape(-1, 1)
        
        # Combine everything: claim_tfidf, evidence_tfidf, similarities
        features = sp.hstack([
            claim_tfidf, 
            evidence_tfidf, 
            similarities,
            claim_lens,
            evidence_lens
        ])
        
        return features
