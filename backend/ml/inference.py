import os
import pickle
import numpy as np
import logging

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

class EvidenceClassifier:
    def __init__(self):
        self.model = None
        self.extractor = None
        self.nli_tokenizer = None
        self.nli_model = None
        
    def load(self):
        model_path = os.path.join(MODELS_DIR, 'evidence_classifier.pkl')
        extractor_path = os.path.join(MODELS_DIR, 'feature_extractor.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(extractor_path):
            raise FileNotFoundError("Model files not found. Please run ml/train.py first.")
            
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        with open(extractor_path, 'rb') as f:
            self.extractor = pickle.load(f)
            
        # Load NLI Cross-Encoder for general clinical and semantic entailment
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            model_name = "cross-encoder/nli-distilroberta-base"
            self.nli_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.nli_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.nli_model.eval()
        except Exception as e:
            logging.warning(f"Could not load NLI transformer model: {e}")
            self.nli_tokenizer = None
            self.nli_model = None
            
    def predict(self, claim, evidence_texts):
        """
        Predict relationship between a single claim and a list of evidence passages.
        Returns a list of dicts with prediction and confidence.
        """
        if not self.model or not self.extractor:
            self.load()
            
        if not evidence_texts:
            return []
            
        # 1. Classical SVM prediction
        claims = np.array([claim] * len(evidence_texts))
        evidences = np.array(evidence_texts)
        X = self.extractor.transform(claims, evidences)
        svm_preds = self.model.predict(X)
        svm_probs = self.model.predict_proba(X)
        svm_classes = list(self.model.classes_)
        
        # 2. Transformer NLI prediction
        nli_results = []
        if self.nli_model and self.nli_tokenizer:
            try:
                import torch
                # Batch tokenization
                inputs = self.nli_tokenizer(
                    [claim] * len(evidence_texts),
                    list(evidence_texts),
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=256
                )
                with torch.no_grad():
                    logits = self.nli_model(**inputs).logits
                    probs = torch.softmax(logits, dim=1).numpy()
                    
                # Cross-encoder distilroberta NLI: 0: contradiction, 1: entailment, 2: neutral
                for p in probs:
                    nli_results.append({
                        "CONTRADICT": float(p[0]),
                        "SUPPORT": float(p[1]),
                        "NEUTRAL": float(p[2])
                    })
            except Exception as e:
                logging.warning(f"NLI batch inference error: {e}")
                nli_results = None
                
        results = []
        c_lower = claim.lower()
        neg_claim = any(w in c_lower for w in ["not", "no", "never", "without", "does not", "did not", "cannot", "fail"])
        
        for idx in range(len(evidence_texts)):
            svm_pred = svm_preds[idx]
            svm_conf = float(np.max(svm_probs[idx]))
            ev_text = evidence_texts[idx].lower()
            
            if nli_results and idx < len(nli_results):
                nli = nli_results[idx]
                p_contra = nli["CONTRADICT"]
                p_supp = nli["SUPPORT"]
                p_neut = nli["NEUTRAL"]
                
                # Check for explicit semantic safety / negation patterns
                safety_reassurance = any(phrase in ev_text for phrase in [
                    "no safety concerns", "did not affect", "does not affect", "no adverse effect", 
                    "no significant difference", "no reduction", "was not associated with", 
                    "does not cause", "did not cause", "safe and effective", "no impact on"
                ])
                
                if safety_reassurance:
                    if neg_claim:
                        pred = "SUPPORT"
                        conf = max(p_supp, 0.88)
                    else:
                        pred = "CONTRADICT"
                        conf = max(p_contra, 0.88)
                elif p_contra > 0.60:
                    pred = "CONTRADICT"
                    conf = p_contra
                elif p_supp > 0.60:
                    pred = "SUPPORT"
                    conf = p_supp
                elif svm_pred in ["SUPPORT", "CONTRADICT"] and svm_conf > 0.60:
                    pred = str(svm_pred)
                    conf = svm_conf
                else:
                    pred = "NEUTRAL"
                    conf = p_neut
            else:
                pred = str(svm_pred)
                conf = svm_conf
                
            results.append({
                "prediction": pred,
                "confidence": float(conf)
            })
            
        return results

# Singleton instance
classifier = EvidenceClassifier()

def classify_evidence(claim, evidence_texts):
    return classifier.predict(claim, evidence_texts)
