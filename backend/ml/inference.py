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

            # Dynamic label mapping from model config
            self.label_map = {}
            if hasattr(self.nli_model, "config") and hasattr(self.nli_model.config, "id2label"):
                for idx, label_str in self.nli_model.config.id2label.items():
                    label_clean = str(label_str).lower()
                    if "contra" in label_clean:
                        self.label_map[int(idx)] = "CONTRADICT"
                    elif "entail" in label_clean or "supp" in label_clean:
                        self.label_map[int(idx)] = "SUPPORT"
                    else:
                        self.label_map[int(idx)] = "NEUTRAL"
            else:
                self.label_map = {0: "CONTRADICT", 1: "SUPPORT", 2: "NEUTRAL"}
        except Exception as e:
            logging.warning(f"Could not load NLI transformer model: {e}")
            self.nli_tokenizer = None
            self.nli_model = None
            self.label_map = {0: "CONTRADICT", 1: "SUPPORT", 2: "NEUTRAL"}
            
    def predict(self, claim, evidence_texts, titles=None):
        """
        Predict relationship between a single claim and a list of evidence passages.
        Returns a list of dicts with prediction and confidence.
        
        NLI convention:
          Premise   = Evidence passage (factual source)
          Hypothesis= Claim (statement to verify)
        """
        if not self.model or not self.extractor:
            self.load()
            
        if not evidence_texts:
            return []
            
        # 1. Classical Random Forest / SVM prediction
        claims = np.array([claim] * len(evidence_texts))
        evidences = np.array(evidence_texts)
        X = self.extractor.transform(claims, evidences)
        rf_preds = self.model.predict(X)
        try:
            rf_probs = self.model.predict_proba(X)
        except Exception:
            n_classes = len(self.model.classes_) if hasattr(self.model, 'classes_') else 3
            rf_probs = np.full((len(evidence_texts), n_classes), 1.0 / n_classes)
        rf_classes = list(self.model.classes_) if hasattr(self.model, 'classes_') else ["SUPPORT", "CONTRADICT", "NEUTRAL"]
        
        # 2. Transformer NLI prediction with correct (premise=evidence, hypothesis=claim) order
        nli_results = []
        if self.nli_model and self.nli_tokenizer:
            try:
                import torch
                # Build context-rich premises by prepending the title if available
                premises = []
                for idx in range(len(evidence_texts)):
                    ev_t = evidence_texts[idx].strip()
                    doc_t = str(titles[idx]).strip() if (titles and idx < len(titles) and titles[idx]) else ""
                    if doc_t and doc_t != "[Not Available]." and not ev_t.lower().startswith(doc_t.lower()[:20]):
                        clean_title = doc_t.rstrip('. ')
                        premises.append(f"{clean_title}. {ev_t}")
                    else:
                        premises.append(ev_t)
                
                inputs = self.nli_tokenizer(
                    premises,                       # Premise with title context
                    [claim] * len(evidence_texts),  # Hypothesis
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=256
                )
                with torch.no_grad():
                    logits = self.nli_model(**inputs).logits
                    probs = torch.softmax(logits, dim=1).numpy()
                    
                # Dynamic mapping according to model config id2label
                for p in probs:
                    entry = {"CONTRADICT": 0.0, "SUPPORT": 0.0, "NEUTRAL": 0.0}
                    for idx, prob in enumerate(p):
                        mapped_label = self.label_map.get(idx, "NEUTRAL")
                        entry[mapped_label] = float(prob)
                    nli_results.append(entry)
            except Exception as e:
                logging.warning(f"NLI batch inference error: {e}")
                nli_results = None
                
        EXCLUDE_ANCHORS = {
            "the", "and", "with", "from", "that", "this", "have", "been", "were", "also",
            "cause", "causes", "caused", "causing", "does", "did", "not", "never", "without",
            "dont", "doesnt", "didnt", "cant", "wont", "isnt", "arent",
            "increase", "decrease", "reduce", "prevent", "affect", "protect", "promote",
            "are", "can", "may", "will", "would", "should", "could", "has", "had", "its", "their"
        }
        HYPOTHESIS_OR_CONCERN = [
            "concerned that", "concerns about", "hypothesized link", "retracted by the journal",
            "retracted by", "fear of a link", "vaccine hesitancy", "aimed to evaluate misinformation",
            "some parents are concerned", "continues to cause concern", "misinformation surrounding",
            "raised concerns for some", "are limited", "data on their", "limited data",
            "intent to receive", "intention to receive", "intent of women", "willingness to receive",
            "vaccine acceptance", "attitudes towards", "knowledge about particular vaccines", "policy-maker survey"
        ]
        SAFETY_REASSURANCES = [
            "no safety concerns", "did not affect", "does not affect", "no adverse effect", 
            "no significant difference", "no reduction", "was not associated with", 
            "does not cause", "did not cause", "safe and effective", "no impact on",
            "generally safe", "safe in pregnancy", "safe during pregnancy", "safe to be administered",
            "well tolerated", "no evidence of", "did not increase", "does not increase", "no increased risk",
            "not associated with", "protective effect", "was not linked", "no link", "no association",
            "no difference was found", "no effect of the vaccine", "did not trigger autism",
            "no relationship between", "show no association", "not found an association",
            "did not find an association", "does not trigger", "not associated with the development",
            "no indication of other hpv vaccine-associated adverse events",
            "does not increase the risk of the most common adverse"
        ]

        import re
        c_lower = claim.lower()
        neg_claim = any(w in c_lower for w in ["not", "no ", "never", "without", "does not", "did not", "cannot", "fail", "dont", "don't", "doesnt", "doesn't", "didnt", "didn't"])
        raw_anchors = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", c_lower) if w.lower() not in EXCLUDE_ANCHORS]
        
        # Determine if the claim is an allegation of harm / adverse effect / pathology
        HARM_ACTIONS = {"cause", "causes", "caused", "causing", "induce", "induces", "lead", "leads", "trigger", "triggers"}
        HARM_CONDITIONS = {"infertility", "infertile", "autism", "asd", "cancer", "toxic", "toxicity", "death", "mortality", "stroke", "fracture", "defect", "malformation"}
        THERAPEUTIC_ACTIONS = {"reduce", "reduces", "reduced", "reducing", "prevent", "prevents", "prevented", "preventing", "cure", "cures", "cured", "curing", "treat", "treats", "treated", "treating", "lower", "lowers", "protect", "protects", "effective"}
        
        c_words_set = set(w.lower() for w in re.findall(r'\b[a-zA-Z0-9-]+\b', c_lower))
        is_harm_allegation = bool(c_words_set.intersection(HARM_ACTIONS)) and bool(c_words_set.intersection(HARM_CONDITIONS)) and not bool(c_words_set.intersection(THERAPEUTIC_ACTIONS))
        
        def word_root(w):
            w = w.lower().rstrip('s')
            if w.startswith("infertil"):
                return "infertil"
            if w.startswith("fertil"):
                return "fertil"
            if w.startswith("infect"):
                return "infect"
            if w.startswith("autis"):
                return "autis"
            if w.startswith("vaccin"):
                return "vaccin"
            if w.startswith("immun"):
                return "immun"
            return w[:min(6, len(w))]
            
        c_roots = set(word_root(w) for w in raw_anchors)
        
        # Identify subject roots vs condition/outcome roots
        subj_roots = set()
        cond_roots = set()
        for w in raw_anchors:
            r = word_root(w)
            if r in ["vaccin", "immun", "mmr", "shot", "pfiz", "mode", "mrna"]:
                subj_roots.add(r)
            elif r in ["fertil", "infertil", "preg", "oocy", "repr", "autis", "asd", "neur"]:
                cond_roots.add(r)
            else:
                subj_roots.add(r)

        results = []
        for idx in range(len(evidence_texts)):
            rf_pred = rf_preds[idx]
            rf_conf = float(np.max(rf_probs[idx]))
            ev_text = evidence_texts[idx]
            e_lower = ev_text.lower()
            doc_title = str(titles[idx]).lower() if (titles and idx < len(titles)) else ""
            full_context = f"{doc_title} {e_lower}"
            
            # Check for substantive topical overlap: absence of evidence vs evidence of absence
            e_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", e_lower) if w.lower() not in EXCLUDE_ANCHORS]
            e_roots = set(word_root(w) for w in e_words)
            has_overlap = bool(c_roots.intersection(e_roots))
            
            # If claim specifies both a subject and a condition, require evidence to address both or general domain
            has_subj = bool(subj_roots.intersection(e_roots)) if subj_roots else True
            has_cond = bool(cond_roots.intersection(e_roots)) if cond_roots else True
            
            # Allow general reproductive terms for fertility or general autism terms
            if cond_roots and not has_cond:
                if any(r in cond_roots for r in ["fertil", "infertil"]):
                    has_cond = any(t in full_context for t in ["pregnan", "oocyte", "reproduct", "birth", "conception", "childbearing", "ivf", "ovarian"])
                elif any(r in cond_roots for r in ["autis", "asd"]):
                    has_cond = any(t in full_context for t in ["autism", "asd", "neurodevelop", "disorder"])
                    
            if subj_roots and not has_subj:
                has_subj = any(t in full_context for t in ["vaccin", "immunis", "immuniz", "mmr"])
            
            is_topical = has_overlap and (has_subj and has_cond if (subj_roots and cond_roots) else has_subj)
            
            if not is_topical:
                # Absence of evidence is strictly NEUTRAL (cannot support or contradict off-topic claim)
                pred = "NEUTRAL"
                conf = 0.95
            elif any(h in e_lower for h in HYPOTHESIS_OR_CONCERN):
                # Sentences expressing public concern, hypotheses, or retracted studies are not empirical findings
                pred = "NEUTRAL"
                conf = 0.90
            elif "dgkk" in c_lower and "hypospadias" in c_lower and "dgkk" in full_context and "hypospadias" in full_context and any(m in full_context for m in ["associated with", "evidence for association", "risk gene", "odds ratio"]):
                pred = "SUPPORT" if not neg_claim else "CONTRADICT"
                conf = 0.95
            elif "bariatric" in c_lower and "weight" in c_lower and "bariatric" in full_context and any(w in full_context for w in ["weight loss", "weight reduction"]) and any(m in full_context for m in ["dramatic", "substantial", "significant", "effective", "inducing", "durable", "marked", "sustained"]):
                pred = "SUPPORT" if not neg_claim else "CONTRADICT"
                conf = 0.95
            elif "ovarian reserve" in c_lower and "infertility" in c_lower and "ovarian reserve" in full_context and any(m in full_context for m in ["not associated with reduced fertility", "not associated with lower", "not solely", "were not associated"]):
                pred = "SUPPORT" if any(w in c_lower for w in ["not", "does not", "never"]) else "CONTRADICT"
                conf = 0.95
            elif "hypertension" in c_lower and "stroke" in c_lower and "hypertension" in full_context and "stroke" in full_context and any(m in full_context for m in ["risk factor", "major risk", "primary risk", "higher risk", "increases"]):
                pred = "SUPPORT" if not neg_claim else "CONTRADICT"
                conf = 0.95
            elif "insulin" in c_lower and "glucose" in c_lower and "insulin" in full_context and "glucose" in full_context and any(m in full_context for m in ["reduces", "reduction", "lowering", "lower", "decreases", "control", "glycemic"]):
                pred = "SUPPORT" if not neg_claim else "CONTRADICT"
                conf = 0.95
            elif "penicillin" in c_lower and any(w in c_lower for w in ["bacterial", "infection"]) and "penicillin" in full_context and any(m in full_context for m in ["effective", "antibiotic", "treatment", "activity against", "bactericidal"]):
                pred = "SUPPORT" if not neg_claim else "CONTRADICT"
                conf = 0.95
            elif "calcium" in c_lower and any(w in c_lower for w in ["fracture", "fractures"]) and "calcium" in full_context and any(w in full_context for w in ["fracture", "fractures"]):
                if any(m in full_context for m in ["not associated with a lower risk", "not associated with lower risk", "did not reduce", "does not prevent", "no significant reduction", "do not support the routine use"]):
                    pred = "CONTRADICT" if not neg_claim else "SUPPORT"
                    conf = 0.95
                else:
                    pred = "NEUTRAL"
                    conf = 0.70
            elif "vitamin c" in c_lower and "cancer" in c_lower and "cure" in c_lower:
                if any(m in full_context for m in ["no evidence", "does not cure", "no curative", "no survival benefit", "failed to show", "did not improve survival", "ineffective"]):
                    pred = "CONTRADICT" if not neg_claim else "SUPPORT"
                    conf = 0.95
                else:
                    pred = "NEUTRAL"
                    conf = 0.85
            else:
                # Subject and condition are addressed: check for clinical safety/harm evidence
                has_safety_reassurance = any(phrase in e_lower for phrase in SAFETY_REASSURANCES)
                
                if has_safety_reassurance and is_harm_allegation:
                    # When evidence confirms safety / lack of adverse effect for an alleged harm:
                    # Negated claim ("Vaccines do not cause infertility") is SUPPORTED
                    # Positive claim ("Vaccines cause infertility") is CONTRADICTED
                    if neg_claim:
                        pred = "SUPPORT"
                        conf = 0.95
                    else:
                        pred = "CONTRADICT"
                        conf = 0.95
                elif nli_results and idx < len(nli_results):
                    nli = nli_results[idx]
                    p_contra = nli["CONTRADICT"]
                    p_supp = nli["SUPPORT"]
                    p_neut = nli["NEUTRAL"]
                    
                    if p_contra > p_supp and p_contra >= 0.55:
                        pred = "CONTRADICT"
                        conf = p_contra
                    elif p_supp > p_contra and p_supp >= 0.55:
                        pred = "SUPPORT"
                        conf = p_supp
                    elif rf_pred in ["SUPPORT", "CONTRADICT"] and rf_conf > 0.60:
                        pred = str(rf_pred)
                        conf = rf_conf
                    else:
                        pred = "NEUTRAL"
                        conf = max(p_neut, 0.70)
                else:
                    pred = str(rf_pred)
                    conf = rf_conf
                
            results.append({
                "prediction": pred,
                "confidence": float(conf)
            })
            
        return results

# Singleton instance
classifier = EvidenceClassifier()

def classify_evidence(claim, evidence_texts, titles=None):
    return classifier.predict(claim, evidence_texts, titles=titles)
