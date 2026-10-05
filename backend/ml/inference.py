import os
import pickle
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

class EvidenceClassifier:
    def __init__(self):
        self.model = None
        self.extractor = None
        
    def load(self):
        model_path = os.path.join(MODELS_DIR, 'evidence_classifier.pkl')
        extractor_path = os.path.join(MODELS_DIR, 'feature_extractor.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(extractor_path):
            raise FileNotFoundError("Model files not found. Please run ml/train.py first.")
            
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        with open(extractor_path, 'rb') as f:
            self.extractor = pickle.load(f)
            
    def predict(self, claim, evidence_texts):
        """
        Predict relationship between a single claim and a list of evidence passages.
        Returns a list of dicts with prediction and confidence.
        """
        if not self.model or not self.extractor:
            self.load()
            
        if not evidence_texts:
            return []
            
        # Repeat the claim for each evidence passage
        claims = np.array([claim] * len(evidence_texts))
        evidences = np.array(evidence_texts)
        
        # Extract features
        X = self.extractor.transform(claims, evidences)
        
        # Predict
        predictions = self.model.predict(X)
        
        # Get confidences using predict_proba (model is SVM with probability=True)
        probs = self.model.predict_proba(X)
        confidences = np.max(probs, axis=1)
            
        results = []
        for pred, conf in zip(predictions, confidences):
            results.append({
                "prediction": str(pred),
                "confidence": float(conf)
            })
            
        return results

# Singleton instance
classifier = EvidenceClassifier()

def classify_evidence(claim, evidence_texts):
    return classifier.predict(claim, evidence_texts)
