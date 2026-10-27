def aggregate_predictions(predictions):
    """
    Project B: Unsupervised Evidence Aggregator.
    
    Aggregates unsupervised K-Means cluster assignments and post-hoc mapped stances
    into a scientifically honest, calibrated final verdict.
    
    Key Design Constraints:
    1. Centroid distances are geometric, NOT class probabilities.
    2. 'UNCERTAIN' stances are treated safely as abstentions.
    3. Final verdicts remain: SUPPORTED, CONTRADICTED, MIXED, INSUFFICIENT.
    """
    support_count = sum(1 for p in predictions if p.get('prediction') == 'SUPPORT')
    contradict_count = sum(1 for p in predictions if p.get('prediction') == 'CONTRADICT')
    neutral_count = sum(1 for p in predictions if p.get('prediction') in ['NEUTRAL', 'UNCERTAIN', None])
    uncertain_count = sum(1 for p in predictions if p.get('prediction') == 'UNCERTAIN')
    
    unique_papers = len(set(
        str(p.get('doc_id') or p.get('document_id') or p.get('source_id') or f"paper_{i}")
        for i, p in enumerate(predictions)
    )) if predictions else 0
    
    counts = {
        "support": support_count,
        "contradict": contradict_count,
        "neutral": neutral_count,
        "uncertain": uncertain_count,
        "papers": unique_papers
    }
    
    if not predictions:
        return {
            "verdict": "INSUFFICIENT",
            "strength": "WEAK",
            "score": 0.0,
            "reason": "No relevant evidence found.",
            "counts": counts,
            "methodology": "Unsupervised K-Means Clustering"
        }
        
    # Aggregate at document level
    doc_scores = {}
    cluster_contributions = {}
    
    for i, p in enumerate(predictions):
        doc_id = str(p.get('doc_id') or p.get('document_id') or p.get('source_id') or f"paper_{i}")
        pred = p.get('prediction', 'NEUTRAL')
        if pred not in ["SUPPORT", "CONTRADICT", "NEUTRAL"]:
            pred = "NEUTRAL"
            
        relevance = float(p.get('relevance_score', 0.5))
        affinity = float(p.get('cluster_affinity', p.get('confidence', 0.5)))
        purity = float(p.get('validation_purity', 0.65))
        cluster_id = p.get('cluster_id', -1)
        
        # Weight = geometric proximity * search relevance * validation cluster purity
        weight = affinity * relevance * purity
        
        if doc_id not in doc_scores:
            doc_scores[doc_id] = {"SUPPORT": 0.0, "CONTRADICT": 0.0, "NEUTRAL": 0.0}
            
        doc_scores[doc_id][pred] = max(doc_scores[doc_id][pred], weight)
        
        if cluster_id != -1:
            cluster_contributions[cluster_id] = cluster_contributions.get(cluster_id, 0.0) + weight
            
    total_support_weight = sum(scores["SUPPORT"] for scores in doc_scores.values())
    total_contradict_weight = sum(scores["CONTRADICT"] for scores in doc_scores.values())
    total_non_neutral = total_support_weight + total_contradict_weight
    
    THRESHOLD = 0.01
    DOMINANCE_RATIO = 2.0
    
    if total_non_neutral < THRESHOLD:
        verdict = "INSUFFICIENT"
        reason = "Retrieved evidence clustered into uninformative or neutral semantic spaces."
        score = float(total_non_neutral)
    else:
        if total_support_weight > 0 and total_contradict_weight > 0:
            ratio = max(total_support_weight, total_contradict_weight) / min(total_support_weight, total_contradict_weight)
        else:
            ratio = float('inf')
            
        if ratio >= DOMINANCE_RATIO:
            if total_support_weight > total_contradict_weight:
                verdict = "SUPPORTED"
                reason = "Evidence clusters predominantly align with supporting literature."
            else:
                verdict = "CONTRADICTED"
                reason = "Evidence clusters predominantly align with contradicting/refuting literature."
        else:
            verdict = "MIXED"
            reason = "Evidence is partitioned across conflicting semantic clusters."
            
        score = float(max(total_support_weight, total_contradict_weight))
        
    supporting_papers = sum(1 for scores in doc_scores.values() if scores["SUPPORT"] > 0)
    contradicting_papers = sum(1 for scores in doc_scores.values() if scores["CONTRADICT"] > 0)
    
    if verdict == "SUPPORTED":
        corroborating = supporting_papers
    elif verdict == "CONTRADICTED":
        corroborating = contradicting_papers
    else:
        corroborating = supporting_papers + contradicting_papers
        
    if corroborating >= 3 and score > 0.10:
        strength = "STRONG"
    elif corroborating >= 2 and score > 0.05:
        strength = "MODERATE"
    else:
        strength = "WEAK"
        
    dominant_cluster = max(cluster_contributions, key=cluster_contributions.get) if cluster_contributions else -1
    
    return {
        "verdict": verdict,
        "strength": strength,
        "score": round(score, 4),
        "reason": reason,
        "counts": counts,
        "methodology": "Unsupervised K-Means (k=3) with SentenceTransformers",
        "dominant_cluster": dominant_cluster,
        "cluster_weights": {str(k): round(v, 4) for k, v in cluster_contributions.items()}
    }
