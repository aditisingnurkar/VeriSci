def build_context(verification_data):
    """
    Builds the grounding context string from the verification dictionary.
    Includes only top 10 most relevant evidence passages to fit in context window.
    """
    claim = verification_data.get("claim", "")
    verdict = verification_data.get("verdict", "")
    reason = verification_data.get("reason", "")
    evidence_list = verification_data.get("evidence", [])
    
    # Sort by relevance and take top 10
    sorted_evidence = sorted(evidence_list, key=lambda x: x.get("relevance_score", 0), reverse=True)[:10]
    
    context_lines = []
    context_lines.append(f"CLAIM: {claim}")
    context_lines.append(f"SYSTEM VERDICT: {verdict}")
    context_lines.append(f"VERDICT REASONING: {reason}")
    context_lines.append("\n--- EVIDENCE FOUND ---")
    
    if not sorted_evidence:
        context_lines.append("No relevant evidence was found.")
    else:
        for ev in sorted_evidence:
            ev_id = ev.get("evidence_id")
            title = ev.get("title")
            source = ev.get("source")
            source_id = ev.get("source_id")
            text = ev.get("evidence_text")
            ctx_before = ev.get("context_before", "")
            ctx_after = ev.get("context_after", "")
            
            # Combine sentences for context
            full_text = " ".join(filter(bool, [ctx_before, text, ctx_after]))
            
            prediction = ev.get("prediction")
            
            context_lines.append(f"<{ev_id}>")
            context_lines.append(f"Source: {source} ({source_id})")
            context_lines.append(f"Title: {title}")
            context_lines.append(f"Model Assessment: {prediction}")
            context_lines.append(f"Text: {full_text}")
            context_lines.append(f"</{ev_id}>")
            context_lines.append("")
            
    return "\n".join(context_lines)
