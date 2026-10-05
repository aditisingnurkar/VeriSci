def aggregate_predictions(predictions):
    """
    Aggregates ML predictions on individual evidence passages into a final verdict.
    """
    support_count = sum(1 for p in predictions if p['prediction'] == 'SUPPORT')
    contradict_count = sum(1 for p in predictions if p['prediction'] == 'CONTRADICT')
    neutral_count = sum(1 for p in predictions if p['prediction'] == 'NEUTRAL')
    
    unique_papers = len(set(
        str(p.get('doc_id') or p.get('document_id') or p.get('source_id') or f"paper_{i}")
        for i, p in enumerate(predictions)
    )) if predictions else 0
    
    counts = {
        "support": support_count,
        "contradict": contradict_count,
        "neutral": neutral_count,
        "papers": unique_papers
    }
    
    if not predictions:
        return {
            "verdict": "INSUFFICIENT",
            "strength": "WEAK",
            "score": 0.0,
            "reason": "No relevant evidence found.",
            "counts": counts
        }
        
    # Aggregate at document level (best evidence per paper)
    doc_scores = {}
    for i, p in enumerate(predictions):
        doc_id = str(p.get('doc_id') or p.get('document_id') or p.get('source_id') or f"paper_{i}")
        pred = p['prediction']
        # Weight each passage's vote by classifier_prob * relevance
        weight = p['confidence'] * p['relevance_score']
        
        if doc_id not in doc_scores:
            doc_scores[doc_id] = {"SUPPORT": 0.0, "CONTRADICT": 0.0, "NEUTRAL": 0.0}
            
        doc_scores[doc_id][pred] = max(doc_scores[doc_id][pred], weight)
        
    total_support_weight = sum(scores["SUPPORT"] for scores in doc_scores.values())
    total_contradict_weight = sum(scores["CONTRADICT"] for scores in doc_scores.values())
    
    total_non_neutral = total_support_weight + total_contradict_weight
    
    # Verdict rules
    THRESHOLD = 0.01  # Minimum non-neutral weight to make a call
    DOMINANCE_RATIO = 2.0  # One side must be at least 2x the other
    
    if total_non_neutral < THRESHOLD:
        verdict = "INSUFFICIENT"
        reason = "Not enough relevant, non-neutral evidence to make a conclusion."
        score = float(total_non_neutral)
    else:
        if total_support_weight > 0 and total_contradict_weight > 0:
            ratio = max(total_support_weight, total_contradict_weight) / min(total_support_weight, total_contradict_weight)
        else:
            ratio = float('inf')
            
        if ratio >= DOMINANCE_RATIO:
            if total_support_weight > total_contradict_weight:
                verdict = "SUPPORTED"
                reason = "Evidence clearly supports the claim."
            else:
                verdict = "CONTRADICTED"
                reason = "Evidence clearly contradicts the claim."
        else:
            verdict = "MIXED"
            reason = "The evidence is conflicting."
            
        score = float(max(total_support_weight, total_contradict_weight))
        
    # Strength logic
    if verdict in ["SUPPORTED", "CONTRADICTED"]:
        if unique_papers >= 3 and score > 0.1:
            strength = "STRONG"
        elif unique_papers >= 2 and score > 0.05:
            strength = "MODERATE"
        else:
            strength = "WEAK"
    elif verdict == "MIXED":
        if unique_papers >= 4:
            strength = "STRONG"
        else:
            strength = "MODERATE"
    else:
        strength = "WEAK"
        
    return {
        "verdict": verdict,
        "strength": strength,
        "score": score,
        "reason": reason,
        "counts": counts
    }
