def aggregate_predictions(predictions):
    """
    Aggregates ML predictions on individual evidence passages into a final verdict.
    
    predictions: list of dicts:
      {
        "evidence": "...",
        "prediction": "SUPPORT" | "CONTRADICT" | "NEUTRAL",
        "confidence": float,
        "relevance_score": float
      }
      
    Returns:
      dict with final_verdict, counts, and aggregated confidence.
    """
    support_count = sum(1 for p in predictions if p['prediction'] == 'SUPPORT')
    contradict_count = sum(1 for p in predictions if p['prediction'] == 'CONTRADICT')
    neutral_count = sum(1 for p in predictions if p['prediction'] == 'NEUTRAL')
    
    total = len(predictions)
    
    if total == 0:
        return {
            "verdict": "INCONCLUSIVE",
            "confidence": 0.0,
            "supporting_count": 0,
            "contradicting_count": 0,
            "neutral_count": 0
        }

    # Weighting logic (optional, but requested to consider ML confidence)
    support_score = sum(p['confidence'] for p in predictions if p['prediction'] == 'SUPPORT')
    contradict_score = sum(p['confidence'] for p in predictions if p['prediction'] == 'CONTRADICT')
    
    # Verdict Rules:
    # If there is strong supporting evidence and little/no contradicting
    if support_score > contradict_score and support_count > 0 and (support_count > contradict_count):
        verdict = "LIKELY SUPPORTED"
        confidence = support_score / (support_score + contradict_score + 1e-9)
    # If there is strong contradicting evidence
    elif contradict_score > support_score and contradict_count > 0 and (contradict_count > support_count):
        verdict = "LIKELY CONTRADICTED"
        confidence = contradict_score / (support_score + contradict_score + 1e-9)
    # If neither (mostly neutral or conflicting)
    else:
        verdict = "INCONCLUSIVE"
        confidence = 0.5 # Neutral confidence

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)
    
    return {
        "verdict": verdict,
        "confidence": round(float(confidence), 2),
        "supporting_count": support_count,
        "contradicting_count": contradict_count,
        "neutral_count": neutral_count
    }
